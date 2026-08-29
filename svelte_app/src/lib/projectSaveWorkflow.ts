import type { OperationStep } from '$lib/components/OperationProgress.svelte';
import { publishProjectPbix, unlinkProjectPbix } from '$lib/powerbi-publish';
import { createProject, updateProject, type ProjectSubmitInput } from '$lib/projects';
import { captureProjectThumbnail, deleteProjectThumbnail, uploadProjectThumbnail } from '$lib/thumbnails';
import {
	replacePendingBodyImages,
	uploadProjectBodyImages,
	type PendingProjectBodyImage
} from '$lib/projectBodyImages';
import { projectInputForPbixReplacement } from '$lib/projectInput';

type ProjectMutationResult = {
	ok: boolean;
	message: string;
	projectId: string | null;
};

export type ProjectSaveWorkflowResult =
	| { ok: true; projectId: string; message: string }
	| { ok: false; projectId: string | null; message: string; projectSaved: boolean };

export type ProjectSaveWorkflowOptions = {
	mode: 'create' | 'edit';
	projectId?: string;
	input: ProjectSubmitInput;
	bodyHtml: string;
	bodyImageFiles: PendingProjectBodyImage[];
	thumbnailFile: File | null;
	pbixFile: File | null;
	setBodyHtml: (html: string) => void;
	syncProjectBodyInput: () => void;
	releaseBodyImageFiles: () => void;
	startOperation: (steps: OperationStep[]) => void;
	setOperationStep: (id: string, progress: number, detail: string) => void;
	failOperation: (detail?: string) => void;
};

export async function runProjectSaveWorkflow(
	options: ProjectSaveWorkflowOptions
): Promise<ProjectSaveWorkflowResult> {
	const { mode, input, projectId, bodyImageFiles, thumbnailFile, pbixFile } = options;
	options.startOperation(buildProjectOperationSteps(options));
	options.setOperationStep('save', 18, '프로젝트 정보를 저장하는 중입니다.');

	const projectUpdateInput = projectInputForPbixReplacement(input, mode, Boolean(pbixFile));
	const result = await saveProject(mode, projectId, projectUpdateInput);
	if (!result.ok || !result.projectId) {
		return fail(options, result.message, null);
	}

	const savedProjectId = result.projectId;
	if (bodyImageFiles.length > 0) {
		const progress = mode === 'create' ? 34 : 32;
		options.setOperationStep('body-image-upload', progress, '본문 이미지를 업로드하는 중입니다.');
		const bodyImageResult = await uploadProjectBodyImages(savedProjectId, bodyImageFiles);
		if (!bodyImageResult.ok || bodyImageResult.urls.length !== bodyImageFiles.length) {
			return fail(options, bodyImageResult.message, savedProjectId);
		}
		options.setBodyHtml(replacePendingBodyImages(options.bodyHtml, bodyImageFiles, bodyImageResult.urls));
		options.syncProjectBodyInput();
		const bodyUpdateInput = projectInputForPbixReplacement(input, mode, Boolean(pbixFile));
		const bodyUpdateResult = await updateProject(savedProjectId, bodyUpdateInput);
		if (!bodyUpdateResult.ok) {
			return fail(options, bodyUpdateResult.message, savedProjectId);
		}
		options.releaseBodyImageFiles();
	}

	if (mode === 'edit' && input.delete_thumbnail && !thumbnailFile && input.thumbnail_mode !== 'capture') {
		options.setOperationStep('thumbnail-delete', 36, '기존 썸네일을 삭제하는 중입니다.');
		const deleteThumbnailResult = await deleteProjectThumbnail(savedProjectId);
		if (!deleteThumbnailResult.ok) {
			return fail(options, deleteThumbnailResult.message, savedProjectId);
		}
	}

	if (mode === 'edit' && input.delete_pbix && !pbixFile) {
		options.setOperationStep('pbix-unlink', 48, '기존 Power BI 게시본 연결을 삭제하는 중입니다.');
		const unlinkResult = await unlinkProjectPbix(savedProjectId);
		if (!unlinkResult.ok) {
			return fail(options, unlinkResult.message, savedProjectId);
		}
	}

	if (thumbnailFile) {
		const progress = mode === 'create' ? 42 : 58;
		options.setOperationStep('thumbnail-upload', progress, '썸네일 이미지를 업로드하는 중입니다.');
		const uploadResult = await uploadProjectThumbnail(savedProjectId, thumbnailFile);
		if (!uploadResult.ok) {
			return fail(options, uploadResult.message, savedProjectId);
		}
	}

	if (pbixFile) {
		const progress = mode === 'create' ? 62 : 72;
		const detail = mode === 'create'
			? 'PBIX 파일을 Power BI Workspace에 게시하는 중입니다.'
			: '새 PBIX 파일을 Power BI Workspace에 게시하는 중입니다.';
		options.setOperationStep('pbix-publish', progress, detail);
		const publishResult = await publishProjectPbix(savedProjectId, pbixFile);
		if (!publishResult.ok) {
			return fail(options, publishResult.message, savedProjectId);
		}
	}

	if (input.thumbnail_mode === 'capture') {
		const progress = mode === 'create' ? 82 : 86;
		options.setOperationStep('thumbnail-capture', progress, '프로젝트 대표 썸네일을 자동 캡처 중입니다.');
		const captureResult = await captureProjectThumbnail(savedProjectId);
		if (!captureResult.ok) {
			return fail(options, captureResult.message, savedProjectId);
		}
	}

	const finishDetail = mode === 'create' ? '프로젝트 등록 요청이 완료되었습니다.' : '프로젝트 수정 요청이 완료되었습니다.';
	options.setOperationStep('finish', 100, finishDetail);
	return { ok: true, projectId: savedProjectId, message: result.message };
}

function buildProjectOperationSteps(options: ProjectSaveWorkflowOptions): OperationStep[] {
	const { mode, input, bodyImageFiles, thumbnailFile, pbixFile } = options;
	const steps: OperationStep[] = [{ id: 'save', label: '프로젝트 정보를 저장합니다.', status: 'pending' }];
	if (bodyImageFiles.length > 0) {
		steps.push({ id: 'body-image-upload', label: '본문 이미지를 업로드합니다.', status: 'pending' });
	}
	if (mode === 'edit' && input.delete_thumbnail && !thumbnailFile && input.thumbnail_mode !== 'capture') {
		steps.push({ id: 'thumbnail-delete', label: '기존 썸네일을 삭제합니다.', status: 'pending' });
	}
	if (mode === 'edit' && input.delete_pbix && !pbixFile) {
		steps.push({ id: 'pbix-unlink', label: '기존 Power BI 연결을 삭제합니다.', status: 'pending' });
	}
	if (thumbnailFile) {
		steps.push({ id: 'thumbnail-upload', label: '썸네일 이미지를 업로드합니다.', status: 'pending' });
	}
	if (pbixFile) {
		steps.push({
			id: 'pbix-publish',
			label: mode === 'create' ? 'PBIX 파일을 Power BI Workspace에 게시합니다.' : '새 PBIX 파일을 Power BI Workspace에 게시합니다.',
			status: 'pending'
		});
	}
	if (input.thumbnail_mode === 'capture') {
		steps.push({ id: 'thumbnail-capture', label: '대표 썸네일을 자동 캡처합니다.', status: 'pending' });
	}
	steps.push({
		id: 'finish',
		label: mode === 'create' ? '프로젝트 등록 요청을 완료합니다.' : '프로젝트 수정 요청을 완료합니다.',
		status: 'pending'
	});
	return steps;
}

async function saveProject(mode: 'create' | 'edit', projectId: string | undefined, input: ProjectSubmitInput) {
	return mode === 'create'
		? createProject(input)
		: projectId
			? updateProject(projectId, input)
			: ({ ok: false, message: '프로젝트 ID가 없습니다.', projectId: null } satisfies ProjectMutationResult);
}

function fail(
	options: ProjectSaveWorkflowOptions,
	message: string,
	projectId: string | null
): ProjectSaveWorkflowResult {
	options.failOperation();
	return {
		ok: false,
		projectId,
		message: options.mode === 'create' && projectId ? `${message} 프로젝트는 등록되었습니다.` : message,
		projectSaved: Boolean(projectId)
	};
}
