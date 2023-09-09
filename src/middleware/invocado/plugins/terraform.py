import glob
import git
import shutil

from .base import Plugin


class Terraform(Plugin):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for plugin in ['Db']:
            setattr(self,
                    plugin.lower(),
                    self.registry.get(plugin)(self.state))

    def add_configs_to_db(self) -> None:
        configs = glob.glob(str(self.db.terraform_dir) + '/**/main.tf', recursive=True)
        to_add = list()
        for config in configs:
            config = config.replace(str(self.db.terraform_dir), '')
            config = config.replace('/main.tf', '')
            config = config.strip('/')
            to_add.append({
                'kind': 'F',
                'description': config
            })
        to_add = [dict(t) for t in {tuple(d.items()) for d in to_add}]
        to_add.sort(key=lambda x: x['description'])
        print(to_add)
        self.db.add_mac_mapping(to_add)

    def clone_repo(self, reset: bool = True) -> None:
        if self.db.terraform_repo in [None, '']:
            self.db.terraform_repo = input("Terraform Repo URL: ")
        try:
            repo = git.Repo(self.db.terraform_dir)
        except (git.exc.NoSuchPathError, git.exc.InvalidGitRepositoryError):
            repo = git.Repo.clone_from(self.db.terraform_repo, self.db.terraform_dir)

        if not hasattr(repo.remotes, 'origin') or self.db.terraform_repo not in repo.remotes.origin.urls:
            shutil.rmtree(self.db.terraform_dir)
            self.clone_repo()

        if reset:
            repo.git.reset('--hard')
            repo.remotes.origin.pull()
