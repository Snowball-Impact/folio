<script lang="ts">
	import { formatDate } from '$lib/format';
	import type { PowerBIContentLink, PowerBIHubTopic } from '$lib/types';

	let { data } = $props();
	const NEWS_PAGE_SIZE = 10;
	const COMMUNITY_PAGE_SIZE = 10;
	let newsPageIndex = $state(0);
	let communityPageIndex = $state(0);

	const heroByTopic: Record<
		PowerBIHubTopic,
		{ eyebrow: string; title: string; body: string; className: string }
	> = {
		news: {
			eyebrow: 'Power BI News',
			title: 'Power BI 소식',
			body: 'Power BI 분석가에게 필요한 Desktop 다운로드, 월간 기능 업데이트, 변경 로그를 원문 링크와 함께 모아 번역 및 요약합니다.',
			className: 'powerbi-news-hero'
		},
		learning: {
			eyebrow: 'Power BI Learning',
			title: 'Power BI 학습 콘텐츠',
			body: '공식 채널과 실무 크리에이터의 Power BI 영상을 모아, DAX, 모델링, 시각화, Fabric 업데이트 흐름을 빠르게 살펴볼 수 있습니다.',
			className: 'powerbi-learning-hero'
		},
		community: {
			eyebrow: 'Power BI Community Blog',
			title: 'Power BI 커뮤니티 소식',
			body: 'Microsoft Fabric Community Blog의 최신 Power BI 글을 모아, 실무에 필요한 핵심만 한국어로 번역하고 요약합니다.',
			className: 'powerbi-community-hero'
		},
		certifications: {
			eyebrow: 'Power BI Certifications',
			title: 'Power BI 자격증, 공식 경로로 바로 확인하세요.',
			body: 'PL-300과 경영정보시각화능력은 Power BI 분석가의 역량을 보여줄 수 있는 대표 자격증입니다. 스터디 클럽에서 시험 준비와 포트폴리오 완성, 웹 배포 피드백까지 함께 이어갈 수 있습니다.',
			className: 'powerbi-cert-hero'
		}
	};

	const hero = $derived(heroByTopic[data.topic]);
	const newsTotalPages = $derived(Math.max(Math.ceil(data.news.length / NEWS_PAGE_SIZE), 1));
	const visibleNews = $derived(
		data.news.slice(newsPageIndex * NEWS_PAGE_SIZE, newsPageIndex * NEWS_PAGE_SIZE + NEWS_PAGE_SIZE)
	);
	const communityTotalPages = $derived(Math.max(Math.ceil(data.community.length / COMMUNITY_PAGE_SIZE), 1));
	const visibleCommunity = $derived(
		data.community.slice(communityPageIndex * COMMUNITY_PAGE_SIZE, communityPageIndex * COMMUNITY_PAGE_SIZE + COMMUNITY_PAGE_SIZE)
	);

	function moveNewsPage(direction: -1 | 1) {
		newsPageIndex = Math.min(Math.max(newsPageIndex + direction, 0), newsTotalPages - 1);
	}

	function moveCommunityPage(direction: -1 | 1) {
		communityPageIndex = Math.min(Math.max(communityPageIndex + direction, 0), communityTotalPages - 1);
	}
</script>

<svelte:head>
	<title>Power BI 콘텐츠 허브 | FOLIO</title>
	<meta name="description" content="Power BI 업데이트, 학습 콘텐츠, 커뮤니티 소식과 자격증 링크를 모아 봅니다." />
</svelte:head>

<section class={`powerbi-hero ${hero.className}`}>
	<div>
		<div class="powerbi-eyebrow">{hero.eyebrow}</div>
		<div class:powerbi-news-title-row={data.topic === 'news'}>
			<h1>{hero.title}</h1>
			{#if data.topic === 'news' && data.desktop}
				<a class="powerbi-hero-cta compact" href={data.desktop.url} target="_blank" rel="noreferrer">
					최신 Desktop 다운로드
				</a>
			{/if}
		</div>
		<p>{hero.body}</p>
		{#if data.topic === 'certifications'}
			<a class="powerbi-hero-cta" href="https://discord.gg/vKb9SKA3k" target="_blank" rel="noreferrer">
				스터디 클럽 참여하기
			</a>
		{/if}
	</div>
	{#if data.topic === 'certifications'}
		<div class="powerbi-cert-hero-visual" aria-label="Power BI 자격증">
			<img class="powerbi-cert-hero-badge" src="/cert-pl300.png" alt="Microsoft Certified Power BI Data Analyst Associate" />
			<img class="powerbi-cert-hero-poster" src="/cert-bi-specialist.jpg" alt="경영정보시각화능력 BI Specialist" />
		</div>
	{:else}
		<div class="powerbi-hero-visual" aria-label={hero.title}>
			<img src="/reference-powerbi-logo-cropped.webp" alt="Power BI" />
		</div>
	{/if}
</section>

{#if data.topic === 'learning'}
	<section class="learning-list">
		{#each data.learning as group, index}
			<details class="learning-section" open={index === 0}>
				<summary>
					<span>{group.category}</span>
					<em>{group.programs.length + group.videos.length}개 콘텐츠</em>
				</summary>
				<div class="content-grid">
					{#each group.programs as item}
						{@render ContentCard(item, 'program')}
					{/each}
					{#each group.videos as item}
						{@render ContentCard(item, 'video')}
					{/each}
				</div>
			</details>
		{:else}
			<div class="empty-panel">아직 수집된 학습 콘텐츠가 없습니다.</div>
		{/each}
	</section>
{:else if data.topic === 'community'}
	<section class="content-list">
		{#each visibleCommunity as item}
			{@render CommunityRow(item)}
		{:else}
			<div class="empty-panel">아직 수집된 커뮤니티 소식이 없습니다.</div>
		{/each}
		{#if data.community.length > COMMUNITY_PAGE_SIZE}
			<div class="news-pagination" aria-label="Power BI 커뮤니티 소식 페이지">
				<button type="button" onclick={() => moveCommunityPage(-1)} disabled={communityPageIndex <= 0} aria-label="이전 커뮤니티 소식">‹</button>
				<div class="news-page-indicator">{communityPageIndex + 1} / {communityTotalPages}</div>
				<button type="button" onclick={() => moveCommunityPage(1)} disabled={communityPageIndex >= communityTotalPages - 1} aria-label="다음 커뮤니티 소식">›</button>
			</div>
		{/if}
	</section>
{:else if data.topic === 'certifications'}
	<section class="cert-grid">
		{#each data.certifications as item}
			{@render CertCard(item)}
		{/each}
	</section>
{:else}
	<section class="news-board">
		{#each visibleNews as item, index}
			<details class="news-release-row">
				<summary>
					<span class="news-row-index">{data.news.length - (newsPageIndex * NEWS_PAGE_SIZE + index)}</span>
					<span class="news-row-label">{item.label}</span>
					<span class="news-expander-title">{item.title}</span>
					{#if item.source_url}
						<a class="news-source-link" href={item.source_url} target="_blank" rel="noreferrer" onclick={(event) => event.stopPropagation()}>원문</a>
					{/if}
				</summary>
				<div class="news-release-body">
					{#if item.video}
						<a class="news-video-card" href={item.video.url} target="_blank" rel="noreferrer">
							<span class="news-video-thumb">
								{#if item.video.image_url}
									<img src={item.video.image_url} alt="" loading="lazy" />
								{/if}
							</span>
							<span class="news-video-copy">
								<span>공식 업데이트 영상</span>
								<strong>{item.video.title}</strong>
							</span>
							<span class="news-video-open">영상 보기</span>
						</a>
					{/if}
					{#if item.bullets.length > 0}
						<ul class="news-summary-list">
							{#each item.bullets as bullet}
								<li>{bullet}</li>
							{/each}
						</ul>
					{/if}
				</div>
			</details>
		{:else}
			<div class="empty-panel">아직 수집된 Power BI 소식이 없습니다.</div>
		{/each}
		{#if data.news.length > NEWS_PAGE_SIZE}
			<div class="news-pagination" aria-label="Power BI 소식 페이지">
				<button type="button" onclick={() => moveNewsPage(-1)} disabled={newsPageIndex <= 0} aria-label="이전 소식">‹</button>
				<div class="news-page-indicator">{newsPageIndex + 1} / {newsTotalPages}</div>
				<button type="button" onclick={() => moveNewsPage(1)} disabled={newsPageIndex >= newsTotalPages - 1} aria-label="다음 소식">›</button>
			</div>
		{/if}
	</section>
{/if}

{#snippet ContentCard(item: PowerBIContentLink, variant: 'program' | 'video')}
	<a class="content-card" class:program={variant === 'program'} href={item.url} target="_blank" rel="noreferrer">
		{#if item.image_url}
			<img src={item.image_url} alt="" loading="lazy" />
		{/if}
		<span>{item.source} · {item.topic}</span>
		<strong>{item.title}</strong>
		<em>{item.summary}</em>
	</a>
{/snippet}

{#snippet CommunityRow(item: PowerBIContentLink)}
	<article class="community-card">
		<div class="community-meta">{formatDate(item.date)} · {item.source}</div>
		<div class="community-title-row">
			<strong>{item.title}</strong>
			<a class="community-link" href={item.url} target="_blank" rel="noreferrer">원문 보기</a>
		</div>
		<div class="community-summary-row">
			<p>{item.summary}</p>
			<div class="content-tags" aria-label="분류">
				<span>{item.topic}</span>
			</div>
		</div>
	</article>
{/snippet}

{#snippet CertCard(item: PowerBIContentLink)}
	<a
		class="cert-card"
		class:pl300={item.source === 'Microsoft Learn'}
		class:kcci={item.source === 'KCCI'}
		href={item.url}
		target="_blank"
		rel="noreferrer"
	>
		<div class="cert-logo" aria-hidden="true">
			<span>{item.source === 'Microsoft Learn' ? 'Microsoft Certified' : 'KCCI'}</span>
			<strong>{item.source === 'Microsoft Learn' ? 'PL-300' : 'BI Specialist'}</strong>
			<em>{item.source === 'Microsoft Learn' ? 'Power BI Data Analyst' : '경영정보시각화능력'}</em>
		</div>
		<div class="cert-name">{item.title}</div>
		<div class="cert-link">공식 페이지 바로가기</div>
	</a>
{/snippet}
{#snippet ContentRow(item: PowerBIContentLink)}
	<a class="content-row" href={item.url} target="_blank" rel="noreferrer">
		<div>
			<span>{item.source} · {formatDate(item.date)}</span>
			<strong>{item.title}</strong>
			<p>{item.summary}</p>
		</div>
		<em>{item.topic}</em>
	</a>
{/snippet}
