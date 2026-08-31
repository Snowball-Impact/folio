<script lang="ts">
import type { ProjectSubmitInput } from '$lib/types';
	import { projectFormTagLabel } from '$lib/projectForm';

	type PlatformOption = {
		key: ProjectSubmitInput['platform'];
		label: string;
	};

	let {
		input = $bindable(),
		platformOptions,
		onSelectThumbnail,
		onSelectPbix,
		hasPowerbiReport = false,
		hasExistingThumbnail = false
	}: {
		input: ProjectSubmitInput;
		platformOptions: readonly PlatformOption[];
		onSelectThumbnail: (event: Event) => void;
		onSelectPbix: (event: Event) => void;
		hasPowerbiReport?: boolean;
		hasExistingThumbnail?: boolean;
	} = $props();

	const tagLabel = $derived(projectFormTagLabel(input.tags, input.platform));
</script>

<section class="project-form-section project-form-overview-section">
	<div class="project-form-overview-grid">
		<div class="project-form-overview-column">
			<header class="project-form-section-heading">
				<h2>기본 정보</h2>
				<p>프로젝트를 한눈에 이해할 수 있는 정보를 입력하세요.</p>
			</header>

			<label>
				<span class="field-label-row"><span>프로젝트명 *</span><button class="field-help" type="button" title="홈 갤러리 카드 제목 영역에 맞춰 최대 48자까지 입력할 수 있습니다." aria-label="프로젝트명 도움말">?</button></span>
				<input bind:value={input.title} maxlength="48" placeholder="예: 서울시 청년 취업 데이터 분석" />
			</label>

			<label>
				<span class="field-label-row"><span>프로젝트 한 줄 소개</span><button class="field-help" type="button" title="홈 갤러리 카드 요약 영역에 맞춰 최대 56자까지 입력할 수 있습니다." aria-label="프로젝트 한 줄 소개 도움말">?</button></span>
				<input bind:value={input.one_liner} maxlength="56" placeholder="핵심 메시지를 한 문장으로 적어주세요." />
			</label>

			<label>
				<span class="field-label-row"><span>{tagLabel}</span><button class="field-help" type="button" title="#은 자동으로 제거되고 쉼표 기준으로 최대 5개까지 저장됩니다." aria-label="태그 도움말">?</button></span>
				<input bind:value={input.tags} placeholder="공공데이터, 시각화, 취업" />
			</label>

			<div class="platform-panel">
				<fieldset class="choice-panel">
					<legend>플랫폼</legend>
					<div class="segmented-options overview-radio-options">
						{#each platformOptions as option}
							<label>
								<input type="radio" bind:group={input.platform} value={option.key} />
								<span>{option.label}</span>
							</label>
						{/each}
					</div>
				</fieldset>

				{#if input.platform === 'powerbi'}
					{#if hasPowerbiReport}
						<label class="delete-option-row">
							<input type="checkbox" bind:checked={input.delete_pbix} />
							<span>기존 Power BI 게시본 연결 삭제</span>
						</label>
					{/if}
					{#if !hasPowerbiReport || input.delete_pbix}
						<div class="overview-file-field pbix-upload-field">
							<label>
								<span>PBIX 파일 업로드</span>
								<input type="file" accept=".pbix" onchange={onSelectPbix} />
								<small>Cloudflare MVP 기본 최대 50MB / 파일 · PBIX</small>
							</label>
							<p class="pbix-upload-warning">개인정보, 사내 데이터, 비공개 고객 정보가 포함된 PBIX는 업로드하지 마세요.</p>
						</div>
					{/if}
				{/if}
			</div>
		</div>

		<div class="project-form-overview-column project-form-resource-column">
			<header class="project-form-section-heading">
				<h2>산출물 링크</h2>
				<p>공개 프로젝트에서 연결할 외부 산출물을 입력하세요.</p>
			</header>

			<label>
				<span class="field-label-row"><span>Embed Code</span><button class="field-help" type="button" title="iframe 코드 전체 또는 https URL을 입력할 수 있습니다." aria-label="Embed Code 도움말">?</button></span>
				<input bind:value={input.power_bi_url} placeholder="https://... 또는 iframe 코드" />
			</label>

			<label>
				<span class="field-label-row"><span>GitHub URL</span><button class="field-help" type="button" title="http:// 또는 https://로 시작하는 주소를 입력하세요." aria-label="GitHub URL 도움말">?</button></span>
				<input bind:value={input.github_url} placeholder="https://github.com/..." />
			</label>

			<label>
				<span class="field-label-row"><span>Web App URL</span><button class="field-help" type="button" title="http:// 또는 https://로 시작하는 주소를 입력하세요." aria-label="Web App URL 도움말">?</button></span>
				<input bind:value={input.report_url} placeholder="https://..." />
			</label>

			<div class="thumbnail-panel">
				<fieldset class="choice-panel thumbnail-choice-panel">
					<legend>썸네일 설정</legend>
					<div class="segmented-options overview-radio-options thumbnail-options">
						<label>
							<input type="radio" bind:group={input.thumbnail_mode} value="auto_cover" />
							<span>기본 커버</span>
						</label>
						<label>
							<input type="radio" bind:group={input.thumbnail_mode} value="upload" />
							<span>이미지 업로드</span>
						</label>
						<label>
							<input type="radio" bind:group={input.thumbnail_mode} value="manual_url" />
							<span>URL 입력</span>
						</label>
						<label>
							<input type="radio" bind:group={input.thumbnail_mode} value="capture" />
							<span>화면 캡처</span>
						</label>
					</div>
				</fieldset>

				{#if hasExistingThumbnail}
					<label class="delete-option-row">
						<input type="checkbox" bind:checked={input.delete_thumbnail} />
						<span>{input.thumbnail_mode === 'capture' ? '기존 캡처본 삭제 후 재캡처' : '기존 썸네일 삭제'}</span>
					</label>
				{/if}

				{#if input.thumbnail_mode === 'upload' && (!hasExistingThumbnail || input.delete_thumbnail)}
					<label class="overview-file-field">
						<span>썸네일 이미지</span>
						<input type="file" accept="image/jpeg,image/png,image/webp" onchange={onSelectThumbnail} />
						<small>최대 5MB / 파일 · JPG, PNG, WebP</small>
					</label>
				{/if}

				{#if input.thumbnail_mode === 'manual_url'}
					<label>
						<span>썸네일 URL</span>
						<input bind:value={input.thumbnail_url} placeholder="https://..." />
					</label>
				{/if}

				{#if input.thumbnail_mode === 'capture'}
					<small>배포 환경에서 캡처 런타임을 명시적으로 켠 경우에만 대표 이미지를 생성합니다.</small>
				{/if}
			</div>
		</div>
	</div>
</section>
