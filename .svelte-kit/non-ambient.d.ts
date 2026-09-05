
// this file is generated — do not edit it


declare module "svelte/elements" {
	export interface HTMLAttributes<T> {
		'data-sveltekit-keepfocus'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-noscroll'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-preload-code'?:
			| true
			| ''
			| 'eager'
			| 'viewport'
			| 'hover'
			| 'tap'
			| 'off'
			| undefined
			| null;
		'data-sveltekit-preload-data'?: true | '' | 'hover' | 'tap' | 'off' | undefined | null;
		'data-sveltekit-reload'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-replacestate'?: true | '' | 'off' | undefined | null;
	}
}

export {};


declare module "$app/types" {
	type MatcherParam<M> = M extends (param : string) => param is (infer U extends string) ? U : string;

	export interface AppTypes {
		RouteId(): "/" | "/about" | "/api" | "/api/comments" | "/api/comments/[id]" | "/api/comments/[id]/email-notification" | "/api/projects" | "/api/projects/[id]" | "/api/projects/[id]/body-image" | "/api/projects/[id]/powerbi-embed" | "/api/projects/[id]/powerbi-publish" | "/api/projects/[id]/thumbnail-capture" | "/api/projects/[id]/thumbnail" | "/login" | "/my" | "/notifications" | "/onboarding" | "/policy" | "/policy/[type]" | "/powerbi" | "/projects" | "/projects/[id]" | "/projects/[id]/edit" | "/references" | "/references/powerbi" | "/references/[platform]" | "/reset-password" | "/signup" | "/submit";
		RouteParams(): {
			"/api/comments/[id]": { id: string };
			"/api/comments/[id]/email-notification": { id: string };
			"/api/projects/[id]": { id: string };
			"/api/projects/[id]/body-image": { id: string };
			"/api/projects/[id]/powerbi-embed": { id: string };
			"/api/projects/[id]/powerbi-publish": { id: string };
			"/api/projects/[id]/thumbnail-capture": { id: string };
			"/api/projects/[id]/thumbnail": { id: string };
			"/policy/[type]": { type: string };
			"/projects/[id]": { id: string };
			"/projects/[id]/edit": { id: string };
			"/references/[platform]": { platform: string }
		};
		LayoutParams(): {
			"/": { id?: string | undefined; type?: string | undefined; platform?: string | undefined };
			"/about": Record<string, never>;
			"/api": { id?: string | undefined };
			"/api/comments": { id?: string | undefined };
			"/api/comments/[id]": { id: string };
			"/api/comments/[id]/email-notification": { id: string };
			"/api/projects": { id?: string | undefined };
			"/api/projects/[id]": { id: string };
			"/api/projects/[id]/body-image": { id: string };
			"/api/projects/[id]/powerbi-embed": { id: string };
			"/api/projects/[id]/powerbi-publish": { id: string };
			"/api/projects/[id]/thumbnail-capture": { id: string };
			"/api/projects/[id]/thumbnail": { id: string };
			"/login": Record<string, never>;
			"/my": Record<string, never>;
			"/notifications": Record<string, never>;
			"/onboarding": Record<string, never>;
			"/policy": { type?: string | undefined };
			"/policy/[type]": { type: string };
			"/powerbi": Record<string, never>;
			"/projects": { id?: string | undefined };
			"/projects/[id]": { id: string };
			"/projects/[id]/edit": { id: string };
			"/references": { platform?: string | undefined };
			"/references/powerbi": Record<string, never>;
			"/references/[platform]": { platform: string };
			"/reset-password": Record<string, never>;
			"/signup": Record<string, never>;
			"/submit": Record<string, never>
		};
		Pathname(): "/" | "/about" | `/api/comments/${string}/email-notification` & {} | `/api/projects/${string}/body-image` & {} | `/api/projects/${string}/powerbi-embed` & {} | `/api/projects/${string}/powerbi-publish` & {} | `/api/projects/${string}/thumbnail-capture` & {} | `/api/projects/${string}/thumbnail` & {} | "/login" | "/my" | "/notifications" | "/onboarding" | "/policy" | `/policy/${string}` & {} | "/powerbi" | `/projects/${string}` & {} | `/projects/${string}/edit` & {} | "/references/powerbi" | `/references/${string}` & {} | "/reset-password" | "/signup" | "/submit";
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): "/cert-bi-specialist.jpg" | "/cert-pl300.png" | "/fonts/pretendard/LICENSE" | "/fonts/pretendard/PretendardVariable.woff2" | "/gapyear-hero-banner.jpg" | "/hero-my-page-v2.webp" | "/hero-preview-home.jpg" | "/hero-submit.webp" | "/logo.webp" | "/reference-datastudio-logo-cropped.webp" | "/reference-powerbi-logo-cropped.webp" | "/reference-streamlit-logo-cropped.webp" | "/reference-tableau-logo-cropped.webp" | "/robots.txt" | "/snowball-impact.webp" | "/vision-snowball.webp" | string & {};
	}
}