# Junkie
### Reset password flow vulnerability scanner

I don't plan to develop any further for now. If you need to add a header or cookie, edit it from the code's comments. Scans for all vulnerabilities in this [write-up](https://omar0x01.medium.com/hubspot-full-account-takeover-in-bug-bounty-4e2047914ab5). I looked at the write-ups but couldn't find anything different. It creates an average of 40 emails.

You can use param miner or arjun's parameters for mass assignment vulnerabilities. Even if you use the --text parameter, give the parameters as below.

## Usage
```python3 junkie.py --help```

**Example:**

```python3 junkie.py -u https://example.com/a/password_reset -s xxxxxxxxxxxxxxx.oast.fun  --post --json -v username+victim@wearehackerone.com -a username+attacker@wearehackerone.com -p '{"email": "victim"}'  -pf param.txt -l dayone.log --options mass```



## **Contact:**
grolar@wearehackerone.com

[twitter](https://twitter.com/YakupSaitByk)
