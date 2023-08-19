import glob
import git
import pprint

from .base import Plugin


class Terraform(Plugin):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for plugin in ['Db']:
            setattr(self,
                    plugin.lower(),
                    self.registry.get(plugin)(self.state))

    def clone_repo(self) -> None:
        if self.db.terraform_repo in [ None, '' ]:
            self.db.terraform_repo = input("Terraform Repo URL: ")
        git.Repo.clone_from(self.db.terraform_repo, self.db.terraform_dir)

    def add_configs_to_db(self) -> None:
        configs = glob.glob(str(self.db.terraform_dir) + '/**/main.tf', recursive=True)
        to_add = list()
        for config in configs:
            config = config.replace(str(self.db.terraform_dir), '')
            config = config.replace('/main.tf', '')
            config = config.strip('/')
            config = config.split('/')
            for i, folder in enumerate(config):
                to_add.append({
                    "position": i,
                    "description": folder
                })
        to_add = [dict(t) for t in {tuple(d.items()) for d in to_add}]
        to_add.sort(key=lambda x: x['position'])
        self.db.add_mac_mapping(to_add)
