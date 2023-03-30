from test_components.simpleperf_component import SimpleperfComponent
from test_components.test_component import TestComponent
from run_simpleperf_without_usb_connection import stop_recording, start_recording


class SimpleperfDisconnectedComponent(SimpleperfComponent):
    def pre_test_fun(self):
        pass

    def loop_pre_test_fun(self):
        status, output = self.adb.run_and_return_output(
            ['shell', 'rm', '/data/local/tmp/perf.data']
        )
        print(f'deleted data with status {status} and output {output}')

    def test_fun(self):
        start_recording(self.sp_args)

    def shutdown_fun(self):
        self.sp_args.perf_data_path = self.perf_data_path + f'-{self.iteration}.data'
        stop_recording(self.sp_args)

    def loop_post_test_fun(self):
        output_path = self.sp_args.perf_data_path.removesuffix('.data') + f'_logs.txt'
        status, output = self.adb.run_and_return_output(['pull', '/data/local/tmp/simpleperf_output', output_path])
        if not status:
            print(output)
        status, output = self.adb.run_and_return_output(['shell', 'rm', '/data/local/tmp/simpleperf_output'])
        if not status:
            print(output)
        super()._build_bincache(self.sp_args.perf_data_path)

    def post_test_fun(self):
        pass
