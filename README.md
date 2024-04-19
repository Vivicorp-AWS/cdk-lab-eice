
# CDK Lab - EC2 Instance Connect Endpoint (EICE)

This project implement EC2 Instance Connect Endpoint deployment with CDK, to provide a safer way to access workloads in private subnets via SSH (port 22) or RDP (port 3389) without IGWs, public IPs, and anything that can be seciruty vulnerability.

Also credit to the post "[EC2 Instance Connect EndpointをCDKで作成してみた](https://dev.classmethod.jp/articles/create-ec2-instance-connect-endpoint-using-cdk-custom-resource/)" written by [アッキー (Akky)](https://dev.classmethod.jp/author/akky/) from [Classmethod (クラスメソッド株式会社)](https://classmethod.jp), most of my work was just rewrite the code with Python.

## Usage

To deploy all components:

```bash
cdk deploy \
  --all \
  --require-approval=never \
  --outputs-file ./cdk.out/outputs.json
```

Connect the EC2 Instance with EC2 Instance Connect Endpoint (Must install [jq](https://jqlang.github.io/jq/) first):

```bash
aws ec2-instance-connect ssh \
  --instance-id $(jq -r ".EICEStack.EC2InstanceID" ./cdk.out/outputs.json) \
  --os-user ec2-user
```

To remove all components:

```bash
cdk destroy -all
```

## Caveats

### Error Occurs when Connect to Instance Using AWS CLI with "Received disconnect from UNKNOWN port 65535:2: Too many authentication failures" Error Message

Please check your SSH Agent's configurations, make sure it won't prevent you from connecting to your EC2 instance with some other processes.

Or add a custom connection option to opt-out CIDR range `10.0.0.0/8` into your SSH client config file (`~/.ssh/config`):

```
Host 10.*.*.*
  IdentityAgent none
```


