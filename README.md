
# CDK Lab - EC2 Instance Connect Endpoint (EICE)

This project implement EC2 Instance Connect Endpoint deployment with CDK, to provide a safer way to access workloads in private subnets via SSH (port 22) or RDP (port 3389) without IGWs, public IPs, and anything that can be seciruty vulnerability.

Also credit to the post "[EC2 Instance Connect EndpointをCDKで作成してみた](https://dev.classmethod.jp/articles/create-ec2-instance-connect-endpoint-using-cdk-custom-resource/)" written by [アッキー (Akky)](https://dev.classmethod.jp/author/akky/) from [Classmethod (クラスメソッド株式会社)](https://classmethod.jp), most of my work was just re-write the code with Python.
