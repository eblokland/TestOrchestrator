from samplers.environment_sampler import EnvironmentSampler
from test_components.test_component import TestComponent


class EnvironmentSamplerComponent(TestComponent):
    def __init__(self, cfg_file):
        self.samp = EnvironmentSampler(cfg_file)

    def pre_test_fun(self):
        if not self.samp.check_installed():
            self.samp.install_pkg()

    def post_test_fun(self):
        self.samp.pull_log()

    def test_fun(self):
        if not self.samp.start_file_log():
            raise RuntimeError(f'failed to start file log!')

    def shutdown_fun(self):
        self.samp.stop_file_log()
