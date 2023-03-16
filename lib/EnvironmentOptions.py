class EnvironmentOptions:
    def __init__(
        self, env: str, region: str, account_id: str, key_pair_name: str
    ) -> None:
        self.env = env
        self.region = region
        self.account_id = account_id
        self.key_pair_name = key_pair_name
