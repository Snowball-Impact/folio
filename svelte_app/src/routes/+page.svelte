<script lang="ts">
	import { onMount } from 'svelte';
	import ProjectRail from '$lib/components/ProjectRail.svelte';

	let { data } = $props();
	const snapshot = $derived(data.snapshot);
	const filters = $derived(data.filters ?? { search: '', tag: '' });
	const visiblePopularTags = $derived(snapshot.popular_tags.slice(0, 10));
	let displayedProjectCount = $state(0);

	onMount(() => {
		const target = snapshot.total_project_count;
		if (!target) {
			displayedProjectCount = 0;
			return;
		}
		const duration = 720;
		let start: number | null = null;
		function tick(timestamp: number) {
			start ??= timestamp;
			const progress = Math.min((timestamp - start) / duration, 1);
			const eased = 1 - Math.pow(1 - progress, 3);
			displayedProjectCount = Math.round(target * eased);
			if (progress < 1) {
				requestAnimationFrame(tick);
			}
		}
		requestAnimationFrame(tick);
	});
	const homeGuideSteps = [
		['01', '공유', '결과물과 제작 맥락을 모두와 공유합니다.'],
		['02', '피드백', '댓글과 반응으로 새로운 관점을 발견합니다.'],
		['03', '발전', '다양한 관점이 모여 인사이트를 개선합니다.']
	] as const;
	const powerBiSteps = [
		['PBIX', '업로드', '보고서 파일을 올립니다.'],
		['WEB', '웹 배포', '브라우저에서 열 수 있게 게시합니다.'],
		['LINK', '공유', '포트폴리오 링크로 전달합니다.']
	] as const;
	const studySteps = [
		['01', '실습', 'Power BI 과제'],
		['02', '웹 배포 및 피드백', '동료 리뷰 반영'],
		['03', '완성', '포트폴리오 정리']
	] as const;

	const heroSlides = [
		{
			eyebrow: 'Project Portfolio Platform',
			titleHtml: 'AI 시대에는 <em>휴먼 인사이트</em>가 자산이다.',
			bodyHtml:
				'FOLIO는 좋은 시각화를 발견하고,<br>직접 경험하며 토론하고 함께 성장하는 커뮤니티입니다.',
			visual: 'preview',
			cta: '내 프로젝트 등록하기',
			href: '/submit',
			target: '_self'
		},
		{
			eyebrow: 'Collective Insight',
			titleHtml: '인사이트는 <em>공유할수록 깊어집니다.</em>',
			bodyHtml:
				'각자의 시각화 경험을 나누고,<br>댓글과 피드백으로 더 나은 관점을 만들어갑니다.',
			visual: 'guide',
			cta: '내 프로젝트 등록하기',
			href: '/submit',
			target: '_self'
		},
		{
			eyebrow: 'Power BI 무료 웹 게시',
			titleHtml: 'Power BI 보고서를 <em>무료로 웹에 게시하세요.</em>',
			bodyHtml:
				'PBIX 파일을 간편하게 게시하고,<br>누구나 열어볼 수 있는 보고서 페이지로 프로젝트를 공유합니다.',
			visual: 'powerbi',
			cta: 'PBIX 보고서 무료 게시하기',
			href: '/submit',
			target: '_self'
		},
		{
			eyebrow: 'Snowball Impact Study Club',
			titleHtml: 'Power BI 데이터 시각화, <em>함께 공부해요.</em>',
			bodyHtml:
				'스터디 클럽에서 함께 실습하고,<br>보고서 디자인과 DAX, 경영정보시각화 실기를 토론하며 성장합니다.',
			visual: 'study',
			cta: '스터디 클럽 참여하기',
			href: 'https://discord.gg/vKb9SKA3k',
			target: '_blank'
		}
	] as const;

	const heroTrackSlides = $derived([...heroSlides, heroSlides[0]]);
</script>

<svelte:head>
	<title>FOLIO</title>
	<meta
		name="description"
		content="좋은 데이터 시각화 프로젝트를 발견하고 직접 경험하는 FOLIO 공개 갤러리"
	/>
</svelte:head>

<section class="home-hero-shell" aria-label="FOLIO 홈 소개">
	<div class="home-hero-viewport">
		<div class="home-hero-track">
			{#each heroTrackSlides as slide}
				<section class:home-guide-hero={slide.visual === 'guide'} class="home-hero-slide">
					<div class="home-copy">
						<div class="home-eyebrow">{slide.eyebrow}</div>
						<h1>{@html slide.titleHtml}</h1>
						<p>{@html slide.bodyHtml}</p>
						<div class="home-actions">
							<a
								class="home-primary-cta"
								href={slide.href}
								target={slide.target}
								rel={slide.target === '_blank' ? 'noopener' : undefined}
							>
								{slide.cta}
							</a>
						</div>
					</div>
					{#if slide.visual === 'preview'}
						<div class="home-hero-preview">
							<img
								class="home-hero-preview-image"
								src="/hero-preview-home.jpg"
								alt="데이터 분석 대시보드와 인사이트 미리보기"
							/>
						</div>
					{:else if slide.visual === 'guide'}
						<div class="home-guide-flow" aria-label="프로젝트 발전 단계">
							{#each homeGuideSteps as step}
								<div class="home-guide-step">
									<div class="home-guide-node">{step[0]}</div>
									<div class="home-guide-card">
										<strong>{step[1]}</strong>
										<p>{step[2]}</p>
									</div>
								</div>
							{/each}
						</div>
					{:else if slide.visual === 'powerbi'}
						<div class="home-guide-flow home-powerbi-flow" aria-label="Power BI 웹 게시 단계">
							{#each powerBiSteps as step}
								<div class="home-guide-step">
									<div class="home-guide-node">{step[0]}</div>
									<div class="home-guide-card">
										<strong>{step[1]}</strong>
										<p>{step[2]}</p>
									</div>
								</div>
							{/each}
						</div>
					{:else}
						<div class="home-guide-flow home-study-flow" aria-label="Power BI 스터디 진행 단계">
							{#each studySteps as step}
								<div class="home-guide-step">
									<div class="home-guide-node">{step[0]}</div>
									<div class="home-guide-card">
										<strong>{step[1]}</strong>
										<p>{step[2]}</p>
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</section>
			{/each}
		</div>
	</div>
	<div class="home-hero-dots" aria-hidden="true">
		{#each heroSlides as _slide}
			<span></span>
		{/each}
	</div>
</section>

{#if data.error}
	<div class="notice">{data.error}</div>
{/if}

<section class="home-browse-panel" aria-label="홈 갤러리 검색과 태그 필터">
	<form method="GET" class="home-browse-form">
		<div class="home-search-heading">
			<h2>
				<span>{displayedProjectCount.toLocaleString('ko-KR')}</span>개의 휴먼 인사이트 프로젝트가 FOLIO에 쌓이고 있어요.
			</h2>
		</div>
		<div class="home-search-row">
			<input
				type="search"
				name="q"
				value={filters.search}
				placeholder="프로젝트명, 태그, 작성자 검색"
				aria-label="프로젝트 검색"
			/>
			{#if filters.tag}
				<input type="hidden" name="tag" value={filters.tag} />
			{/if}
			<button type="submit">검색</button>
		</div>
	</form>
	<div class="home-tag-row" aria-label="인기 태그 TOP10">
		<div class="home-tag-list">
			<a class:active={!filters.tag} href={filters.search ? `/?q=${encodeURIComponent(filters.search)}` : '/'}>전체</a>
			{#each visiblePopularTags as tag}
				<a
					class:active={filters.tag === tag}
					href={`/?${new URLSearchParams({ ...(filters.search ? { q: filters.search } : {}), tag }).toString()}`}
				>
					{tag}
				</a>
			{/each}
		</div>
		<div class="home-popular-tag-label">인기 태그 TOP10</div>
	</div>
</section>

<ProjectRail
	title="새로 공개된 프로젝트"
	description="최근 등록된 Power BI 프로젝트를 먼저 살펴보세요."
	projects={snapshot.recent_projects}
	emptyMessage="아직 공개된 프로젝트가 없습니다. 첫 프로젝트를 등록해 갤러리를 열어보세요."
/>

<ProjectRail
	title="조회수가 높은 프로젝트"
	description="많이 열린 프로젝트를 빠르게 훑어보세요."
	projects={snapshot.viewed_projects}
	emptyMessage="조회수 순위는 프로젝트가 공개되면 자동으로 채워집니다."
/>

<ProjectRail
	title="좋아요를 받은 프로젝트"
	description="반응이 쌓인 프로젝트를 이어서 확인해보세요."
	projects={snapshot.liked_projects}
	emptyMessage="좋아요를 받은 프로젝트가 아직 없습니다. 좋은 시각화에 첫 반응을 남겨보세요."
/>
