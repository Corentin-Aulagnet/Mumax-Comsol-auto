import MumaxPipeline
import ComsolMumaxPipeline


if __name__=="__main__":
    ##Test mumaxPipeline
    MumaxPipeline.StartPipeline("tests/MumaxPipeline/config_test.yml",60,10800,test=True)
    ##Test ComsolMumaxPipeline
    ComsolMumaxPipeline.StartPipeline("tests/ComsolMumaxPipeline/config_test.yml",60,10800,test=True)
    ##Test

