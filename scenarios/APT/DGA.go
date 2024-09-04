package apt

import (
	"crypto/md5"
	"fmt"
	"strconv"
	"time"
)

func genDomain(seed string, tld string) string {
	timestamp := time.Now().Unix() / (30 * 60)
	// use simple addition to combine seed and timestamp
	hashInput := seed + strconv.FormatInt(timestamp, 10)
	hash := md5.Sum([]byte(hashInput))
	return fmt.Sprintf("%x%s", hash[:7], tld)	
}

