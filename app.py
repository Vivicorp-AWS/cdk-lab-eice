#!/usr/bin/env python3
import os

import aws_cdk as cdk

from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    custom_resources as cr,
    aws_iam as iam,
    CfnOutput,
)
from constructs import Construct

app = cdk.App()

# Ref: https://dev.classmethod.jp/articles/create-ec2-instance-connect-endpoint-using-cdk-custom-resource/
class EICEStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a VPC with 2 private isolated subnets
        vpc = ec2.Vpc(
            self, "EICEVPC",
            max_azs=2, 
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="protected",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
            ],
        )

        # Create a Security Group for EICE
        sg_eice = ec2.SecurityGroup(
            self, "EICESecurityGroup",
            vpc=vpc,
            allow_all_outbound=False,
        )

        # Create a Security Group for EC2 Instance
        sg_ec2 = ec2.SecurityGroup(
            self, "EC2SecurityGroup",
            vpc=vpc,
        )

        # Allow SSH from EICE to EC2 Instance
        sg_eice.add_egress_rule(
            peer=sg_ec2,
            connection=ec2.Port.tcp(22),
        )
        
        # Allow SSH from EC2 Instance to EICE
        sg_ec2.add_ingress_rule(
            peer=sg_eice,
            connection=ec2.Port.tcp(22),
        )

        # Create a EC2 Instance
        bastion = ec2.Instance(
            self, "EICEBastion",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC,),
            instance_type=ec2.InstanceType("g4dn.xlarge"),
            machine_image=ec2.MachineImage.generic_linux({'ap-northeast-1': 'ami-0dadff2c5c2f5f1b7'}),
            block_devices=[
                ec2.BlockDevice(device_name="/dev/xvda", volume=ec2.BlockDeviceVolume.ebs(30))
                ],
            security_group=sg_ec2,
        )
        
        # Create EICE Instance Connect Endpoint with CDK L1 construct
        eice = ec2.CfnInstanceConnectEndpoint(
            self, "EC2InstanceConnectionEndpoint",
            subnet_id=vpc.select_subnets(subnet_type=ec2.SubnetType.PUBLIC).subnet_ids[0],
            security_group_ids=[sg_eice.security_group_id],
            preserve_client_ip=True,
        )

        # (Deprecated) Create a Custom Resource for EICE Instance Connect Endpoint
        # eice = cr.AwsCustomResource(
        #     self, "EC2InstanceConnectionEndpoint",
        #     install_latest_aws_sdk=True,
        #     # Ref 1: https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_CreateInstanceConnectEndpoint.html
        #     # Ref 2: https://docs.aws.amazon.com/AWSJavaScriptSDK/latest/AWS/EC2.html#createInstanceConnectEndpoint-property
        #     on_update=cr.AwsSdkCall(
        #         service="EC2",
        #         action="createInstanceConnectEndpoint",
        #         parameters={
        #             "DryRun": False,
        #             "SubnetId": vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED).subnet_ids[0],
        #             "SecurityGroupIds": [sg_eice.security_group_id],
        #             "PreserveClientIp": True,
        #         },
        #         physical_resource_id=cr.PhysicalResourceId.from_response("InstanceConnectEndpoint.InstanceConnectEndpointId")
        #     ),
        #     # Ref 1: https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DeleteInstanceConnectEndpoint.html
        #     # Ref 2: https://docs.aws.amazon.com/AWSJavaScriptSDK/latest/AWS/EC2.html#deleteInstanceConnectEndpoint-property
        #     on_delete=cr.AwsSdkCall(
        #         service="EC2",
        #         action="deleteInstanceConnectEndpoint",
        #         parameters={
        #             "DryRun": False,
        #             "InstanceConnectEndpointId": cr.PhysicalResourceIdReference(),
        #         }
        #     ),
        #     policy=cr.AwsCustomResourcePolicy.from_statements(statements=[
        #             iam.PolicyStatement(
        #                 actions=[
        #                     "ec2:CreateInstanceConnectEndpoint",
        #                     "ec2:CreateNetworkInterface",
        #                     "ec2:CreateTags",
        #                     "ec2:DeleteInstanceConnectEndpoint",
        #                 ],
        #                 resources=["*"],
        #             ),  
        #         ],
        #     )
        # )

eice_stack = EICEStack(app, "EICEGPUStack")

app.synth()
