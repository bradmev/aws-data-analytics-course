#!/usr/bin/env python

from constructs import Construct
from cdktf import TerraformOutput

from lib.EnvironmentOptions import EnvironmentOptions
from imports.vpc import Vpc


class VpcOptions:
    def __init__(
        self,
        name: str,
        cidr: str,
        azs: list[str],
        public_subnets: list[str],
        private_subnets: list[str],
        single_nat_gateway: bool,
        enable_nat_gateway: bool,
        one_nat_gateway_per_az: bool,
    ) -> None:
        self.name = name
        self.cidr = cidr
        self.azs = azs
        self.public_subnets = public_subnets
        self.private_subnets = private_subnets
        self.single_nat_gateway = single_nat_gateway
        self.enable_nat_gateway = enable_nat_gateway
        self.one_nat_gateway_per_az = one_nat_gateway_per_az


class CustomVpc(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        options: EnvironmentOptions,
        vpc_opts: VpcOptions,
    ):
        super().__init__(scope, id)

        self.vpc = Vpc(
            self,
            "vpc",
            name=vpc_opts.name,
            cidr=vpc_opts.cidr,
            azs=vpc_opts.azs,  # ["us-west-2a", "us-west-2b", "us-west-2c"],
            private_subnets=vpc_opts.private_subnets,  # ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"],
            public_subnets=vpc_opts.public_subnets,  # ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"],
            single_nat_gateway=vpc_opts.single_nat_gateway,
            enable_nat_gateway=vpc_opts.enable_nat_gateway,  # True,
            one_nat_gateway_per_az=vpc_opts.one_nat_gateway_per_az,
        )

        TerraformOutput(self, "vpc_id", value=self.vpc.vpc_id_output)

        TerraformOutput(
            self, "vpc_private_subnets", value=self.vpc.private_subnets_output
        )
