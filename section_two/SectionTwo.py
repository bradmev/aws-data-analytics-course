from cdktf import Resource, Token, Fn
from constructs import Construct

from imports.aws.security_group import SecurityGroup
from imports.aws.security_group_rule import SecurityGroupRule

from lib.CustomBucket import CustomBucket, BucketOptions
from lib.EnvironmentOptions import EnvironmentOptions
from lib.EnvironmentOptions import EnvironmentOptions
from lib.CustomVpc import CustomVpc, VpcOptions
from lib.CustomLambda import CustomLambda, LambdaOptions
from lib.CustomFirehose import CustomFirehose, FirehoseOptions
from lib.CustomInstance import CustomInstance, InstnaceOptions
from lib.CustomIamInstanceProfile import (
    CustomIamInstanceProfile,
    IamInstnaceProfileOptions,
)


class SectionTwo(Resource):
    def __init__(self, scope: Construct, id: str, options: EnvironmentOptions):
        self.options = options
        super().__init__(scope, id)

        #  example bucket
        # bucket_opts = BucketOptions(name="bucket-name-unique-213452823", force_destroy=True)
        # storage = CustomBucket(self, "id-string2", options, bucket_options=bucket_opts)

        vpc_opts = VpcOptions(
            name="section-one-vpc",
            cidr="10.0.0.0/16",
            azs=["us-east-1a"],
            public_subnets=["10.0.101.0/24"],
            private_subnets=["10.0.1.0/24"],
            single_nat_gateway=True,
            enable_nat_gateway=True,
            one_nat_gateway_per_az=True,
        )

        self.custom_vpc = CustomVpc(self, "vpc", options=options, vpc_opts=vpc_opts)

        firehose_opts = FirehoseOptions(
            name="PurchaseLogs",
        )

        self.custom_firehose = CustomFirehose(
            self, "firehose", self.options, firehose_options=firehose_opts
        )

        boot_script = """
#!/bin/bash
sudo yum install -y aws-kinesis-agent
wget http://media.sundog-soft.com/AWSBigData/LogGenerator.zip
unzip LogGenerator.zip
chmod a+x LogGenerator.py
sudo mkdir /var/log/cadabra
sudo cat << EOF > /etc/aws-kinesis/agent.json
{
    "cloudwatch.emitMetrics": true,
    "flows": [
        {
            "filePattern": "/var/log/cadabra/*.log",
            "deliveryStream": "PurchaseLogs"
        }
    ]
}
EOF
sudo service aws-kinesis-agent start
sudo chkconfig aws-kinesis-agent on
sudo ./LogGenerator.py 50000
# section three consumer script
sudo mkdir /opt/course_content
wget http://media.sundog-soft.com/AWSBigData/Consumer.py
sudo mv Consumer.pyh /opt/course_content
        """

        instance_profile = CustomIamInstanceProfile(
            self,
            "profile",
            options=options,
            iam_instance_profile_options=IamInstnaceProfileOptions(
                name="ec2-admin", arns=["arn:aws:iam::aws:policy/AdministratorAccess"]
            ),
        )

        instance_sec_group = SecurityGroup(
            self,
            "security-group",
            vpc_id=self.custom_vpc.vpc.vpc_id_output,
        )
        SecurityGroupRule(
            self,
            "ssh-in",
            type="ingress",
            security_group_id=instance_sec_group.id,
            from_port=22,
            to_port=22,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        )

        SecurityGroupRule(
            self,
            "http-out",
            type="egress",
            security_group_id=instance_sec_group.id,
            from_port=80,
            to_port=80,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        )
        SecurityGroupRule(
            self,
            "https-out",
            type="egress",
            security_group_id=instance_sec_group.id,
            from_port=443,
            to_port=443,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        )

        subnets_token_list = Token().as_list(self.custom_vpc.vpc.public_subnets_output)
        subnet = Fn.element(subnets_token_list, 0)

        instance_opts = InstnaceOptions(
            name="PurchaseLogs",
            instance_type="t3.micro",
            key_name=options.key_pair_name,
            user_data=boot_script,
            iam_instance_profile_name=instance_profile.iam_instance_profile.name,
            ami="ami-005f9685cb30f234b",
            subnet_id=subnet,
            associate_public_ip_address=True,
            security_groups=[instance_sec_group.id],
        )

        self.custom_instance = CustomInstance(
            self, "instance", options=options, instance_options=instance_opts
        )
