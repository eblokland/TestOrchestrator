from samplers.environment_sampler import EnvironmentSampler
from test_components.test_component import TestComponent


class EnvironmentSamplerComponent(TestComponent):
    def __init__(self, cfg_file):
        self.samp = EnvironmentSampler(cfg_file)

    def pre_test_fun(self):
        if not self.samp.check_installed():
            self.samp.install_pkg()
        self.env_sampler_filename = self.samp.outfilename
        self.loop_counter = 1

    def loop_pre_test_fun(self):
        self.samp.outfilename = self.env_sampler_filename + f'-{self.loop_counter}'

    def loop_post_test_fun(self):
        self.loop_counter += 1
        self.samp.pull_log(log_things=True)

    def test_fun(self):
        if not self.samp.start_file_log():
            raise RuntimeError(f'failed to start file log!')

    def shutdown_fun(self):
        self.samp.stop_file_log()
