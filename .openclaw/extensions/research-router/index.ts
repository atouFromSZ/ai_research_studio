import { spawn } from "child_process";
import * as path from "path";
import * as os from "os";

function runPythonCommand(commandText: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const projectRoot = path.join(os.homedir(), "studio/projects/ai_research_studio");
    const pythonPath = path.join(projectRoot, ".venv", "bin", "python");

    const child = spawn(
      pythonPath,
      ["-m", "ai_research_studio.cli_router", commandText],
      {
        cwd: projectRoot,
        env: {
          ...process.env,
          PYTHONPATH: "src",
        },
      }
    );

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (data) => {
      stdout += data.toString();
    });

    child.stderr.on("data", (data) => {
      stderr += data.toString();
    });

    child.on("close", (code) => {
      if (code === 0) {
        resolve(stdout.trim());
      } else {
        reject(
          new Error(
            `Python router 执行失败，exit=${code}\nSTDERR:\n${stderr}\nSTDOUT:\n${stdout}`
          )
        );
      }
    });

    child.on("error", (err) => {
      reject(err);
    });
  });
}

export default function (api: any) {
  api.registerCommand({
    name: "dailygen",
    description: "生成日报",
    requireAuth: true,
    handler: async () => {
      const text = await runPythonCommand("生成日报");
      return { text };
    },
  });

  api.registerCommand({
    name: "dailyview",
    description: "查看最新日报",
    requireAuth: true,
    handler: async () => {
      const text = await runPythonCommand("查看最新日报");
      return { text };
    },
  });

  api.registerCommand({
    name: "dailysummary",
    description: "总结最新日报",
    requireAuth: true,
    handler: async () => {
      const text = await runPythonCommand("总结最新日报");
      return { text };
    },
  });

  api.registerCommand({
    name: "macro",
    description: "查看大行情简报",
    requireAuth: true,
    handler: async () => {
      const text = await runPythonCommand("查看大行情简报");
      return { text };
    },
  });

  api.registerCommand({
    name: "project",
    description: "查看项目状态",
    acceptsArgs: true,
    requireAuth: true,
    handler: async (ctx: any) => {
      const projectName = (ctx.args || "").trim();
      if (!projectName) {
        return { text: "用法：/project <项目名>" };
      }
      const text = await runPythonCommand(`查看项目 ${projectName}`);
      return { text };
    },
  });
}