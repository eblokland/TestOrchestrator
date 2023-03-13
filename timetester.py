from typing import List

from simpleperf_report_lib import ReportLib, SampleStruct, EventStruct


class PythonSample(object):
    def __init__(self, obj: SampleStruct, ev: EventStruct):
        self.time: int = obj.time
        self.cpu: int = obj.cpu
        self.tid : int = obj.tid
        self.period: int = obj.period
        self.event = ev.name

def doTheThing():
    lib = ReportLib()
    lib.SetRecordFile('/Users/erikbl/Documents/Scratch/testsimpleperf/runas3.data')
    cpu_str = 'on-off-cpu'
    if cpu_str in lib.GetSupportedTraceOffCpuModes():
        lib.SetTraceOffCpuMode(cpu_str)
    sampleList : List[PythonSample] = [PythonSample(lib.GetNextSample(), lib.GetEventOfCurrentSample())]
    while lib.GetNextSample() is not None:
        sampleList.append(PythonSample(lib.GetCurrentSample(), lib.GetEventOfCurrentSample()))

    sampleList.sort(key=lambda s: s.time)
    cpufiltered = []
    tid = sampleList[3].tid
    for samp in sampleList:
        if samp.cpu == 2: #samp.tid == tid:
            cpufiltered.append(samp)

    prevTime = 0
    for i in range(1, len(cpufiltered)):
        samp = cpufiltered[i-1]
        next = cpufiltered[i]
        actualPeriod = next.time - samp.time
        print('Cpu = ' + str(samp.cpu) + ' claimed period = ' + str(samp.period) + ' actual = ' + str(actualPeriod) + ' event name = ' + str(samp.tid))



    #for samp in sampleList:
        #if(samp.event == 'task-clock'):
         #   continue
        #if samp.cpu != 0:
            #print('continued')
         #   continue
    #    delta = samp.time - prevTime
    #    print('cpu = ' + str(samp.cpu) + ' delta = ' + str(delta) + ' period = ' + str(samp.period))
    #    prevTime = samp.time
    print(lib.GetRecordCmd())
    lib.Close()




if __name__ == '__main__':
    doTheThing()

