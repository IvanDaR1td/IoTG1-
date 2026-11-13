"""Regenerate both MicroPython and CPython modules from the actual .proto."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from google.protobuf import descriptor_pb2
from google.protobuf.compiler import plugin_pb2

ROOT = Path(__file__).resolve().parents[1]


def main():
    test_output = ROOT / "tests" / "generated"
    test_output.mkdir(parents=True, exist_ok=True)
    compiler = [shutil.which("protoc")] if shutil.which("protoc") else [
        sys.executable, "-m", "grpc_tools.protoc"]
    with tempfile.TemporaryDirectory() as temp:
        descriptors = Path(temp) / "schema.pb"
        subprocess.run(compiler + ["-I", str(ROOT),
            "--descriptor_set_out=" + str(descriptors),
            "--python_out=" + str(test_output), "telemetry.proto"],
            cwd=ROOT, check=True)
        schema = descriptor_pb2.FileDescriptorSet.FromString(descriptors.read_bytes())
        request = plugin_pb2.CodeGeneratorRequest()
        request.file_to_generate.append("telemetry.proto")
        request.proto_file.extend(schema.file)
        # Invoke the real plugin with protoc's request/response format. This also
        # works on Windows without requiring an executable Python shebang.
        result = subprocess.run([sys.executable, str(ROOT / "tools/uprotobuf_plugin.py")],
            input=request.SerializeToString(), stdout=subprocess.PIPE,
            cwd=temp, check=True)
        response = plugin_pb2.CodeGeneratorResponse.FromString(result.stdout)
        if response.error:
            raise RuntimeError(response.error)
        if len(response.file) != 1 or response.file[0].name != "telemetry_upb2.py":
            raise RuntimeError("Unexpected compiler output")
        (ROOT / response.file[0].name).write_text(response.file[0].content, encoding="utf-8")
    print("Generated telemetry_upb2.py and tests/generated/telemetry_pb2.py")


if __name__ == "__main__":
    main()
