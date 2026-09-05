import { o as loadProjectEmbedState } from "../../../../../../chunks/projects.js";
import { n as getPowerBIEmbedConfig, t as PowerBIServiceError } from "../../../../../../chunks/powerbi.js";
import { json } from "@sveltejs/kit";
//#region routes/api/projects/[id]/powerbi-embed/+server.ts
async function GET({ params }) {
	const projectId = params.id;
	const projectState = await loadProjectEmbedState(projectId);
	const project = projectState.state;
	if (!project || project.status === "deleted" || !project.is_public) return json({ error: projectState.error || "프로젝트를 찾을 수 없습니다." }, { status: 404 });
	if (project.status !== "published" || project.project_type !== "powerbi") return json({ error: "Power BI 임베드를 사용할 수 없는 프로젝트입니다." }, { status: 409 });
	try {
		const config = await getPowerBIEmbedConfig(projectId);
		if (!config) return json({ error: "Power BI Report 메타데이터가 없습니다." }, { status: 404 });
		return json(config);
	} catch (error) {
		if (error instanceof PowerBIServiceError) return json({
			error: error.message,
			error_code: error.code,
			upstream_status: error.upstreamStatus,
			upstream_code: error.upstreamCode
		}, { status: error.status });
		return json({
			error: "Power BI Embed Token 발급 중 오류가 발생했습니다.",
			error_code: "PBI_UNKNOWN"
		}, { status: 500 });
	}
}
//#endregion
export { GET };
