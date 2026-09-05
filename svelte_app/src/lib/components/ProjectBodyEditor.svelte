<script lang="ts">
import { onDestroy, onMount } from 'svelte';
import type { Editor as TiptapEditor } from '@tiptap/core';
import ProjectRichContent from './ProjectRichContent.svelte';
import RichEditorIcon from './RichEditorIcon.svelte';

	type BodyImageFileChange = (file: File, objectUrl: string) => void;

	let {
		value,
		onChange,
		onImageFile = (() => undefined)
	}: {
		value: string;
		onChange: (html: string) => void;
		onImageFile?: BodyImageFileChange;
	} = $props();

	let element = $state<HTMLDivElement | null>(null);
	let editor = $state<TiptapEditor | null>(null);
	let NodeSelectionConstructor: typeof import('@tiptap/pm/state').NodeSelection | null = null;
	let previewHtml = $state('');
	let lastEmittedHtml = '';
	type BlockFormat = 'paragraph' | 'heading1' | 'heading2' | 'heading3' | 'heading4' | 'heading5' | 'heading6';
	let blockFormat = $state<BlockFormat>('paragraph');
	let imageInput = $state<HTMLInputElement | null>(null);

	function syncBlockFormat(instance: TiptapEditor | null = editor) {
		if (!instance) {
			return;
		}
		blockFormat = instance.isActive('heading', { level: 2 })
			? 'heading2'
			: instance.isActive('heading', { level: 1 })
				? 'heading1'
				: instance.isActive('heading', { level: 3 })
					? 'heading3'
					: instance.isActive('heading', { level: 4 })
						? 'heading4'
						: instance.isActive('heading', { level: 5 })
							? 'heading5'
							: instance.isActive('heading', { level: 6 })
								? 'heading6'
								: 'paragraph';
	}

	onMount(() => {
		previewHtml = value;
		if (!element) {
			return;
		}
		let cancelled = false;
		async function initializeEditor() {
			const [
				{ Editor, Extension },
				{ default: Color },
				{ NodeSelection },
				{ default: Image },
				{ default: Highlight },
				{ default: Link },
				{ default: Mathematics },
				{ default: Placeholder },
				{ default: Subscript },
				{ default: Superscript },
				{ TextStyle },
				{ default: FontSize },
				{ default: FontFamily },
				{ default: TextAlign },
				{ default: Underline },
				{ StarterKit }
			] = await Promise.all([
				import('@tiptap/core'),
				import('@tiptap/extension-color'),
				import('@tiptap/pm/state'),
				import('@tiptap/extension-image'),
				import('@tiptap/extension-highlight'),
				import('@tiptap/extension-link'),
				import('@tiptap/extension-mathematics'),
				import('@tiptap/extension-placeholder'),
				import('@tiptap/extension-subscript'),
				import('@tiptap/extension-superscript'),
				import('@tiptap/extension-text-style'),
				import('@tiptap/extension-text-style/font-size'),
				import('@tiptap/extension-font-family'),
				import('@tiptap/extension-text-align'),
				import('@tiptap/extension-underline'),
				import('@tiptap/starter-kit')
			]);
			if (cancelled || !element) {
				return;
			}
			NodeSelectionConstructor = NodeSelection;
			const BlockIndent = Extension.create({
				name: 'blockIndent',
				addGlobalAttributes() {
					return [
						{
							types: ['paragraph', 'heading'],
							attributes: {
								indent: {
									default: 0,
									parseHTML: (element: HTMLElement) => Number(element.dataset.indent ?? 0) || 0,
									renderHTML: (attributes: { indent?: number }) => {
										const indent = Math.max(0, Math.min(6, Number(attributes.indent) || 0));
										return indent ? { 'data-indent': String(indent), style: `margin-left: ${indent * 24}px` } : {};
									}
								}
							}
						}
					];
				}
			});
			editor = new Editor({
				element,
				extensions: [
					StarterKit.configure({
						heading: { levels: [1, 2, 3, 4, 5, 6] },
						link: false,
						underline: false
					}),
					BlockIndent,
					TextAlign.configure({
						types: ['heading', 'paragraph']
					}),
					Underline,
					Subscript,
					Superscript,
					TextStyle,
					FontSize,
					Color.configure({ types: ['textStyle'] }),
					FontFamily.configure({ types: ['textStyle'] }),
					Highlight.configure({ multicolor: true }),
					Image.configure({ allowBase64: false, inline: false }),
					Mathematics.configure({ katexOptions: { throwOnError: false } }),
					Link.configure({
						openOnClick: false,
						HTMLAttributes: { rel: 'noopener noreferrer', target: '_blank' }
					}),
					Placeholder.configure({
						placeholder: '프로젝트의 문제 정의, 사용 데이터, 분석 과정, 핵심 인사이트를 작성하세요.'
					})
				],
				content: value,
				onSelectionUpdate: ({ editor: currentEditor }) => syncBlockFormat(currentEditor),
				onUpdate: ({ editor }) => {
					syncBlockFormat(editor);
					previewHtml = editor.getHTML();
					lastEmittedHtml = previewHtml;
					onChange(previewHtml);
				}
			});
			syncBlockFormat(editor);
		}
		void initializeEditor();
		return () => {
			cancelled = true;
		};
	});

	$effect(() => {
		if (!editor || editor.isDestroyed || editor.getHTML() === value || editor.getHTML() === lastEmittedHtml) {
			return;
		}
		editor.commands.setContent(value, { emitUpdate: false });
		previewHtml = value;
		syncBlockFormat(editor);
	});

	onDestroy(() => {
		editor?.destroy();
	});

	function run(command: () => boolean) {
		const result = command();
		editor?.commands.focus();
		return result;
	}

	function setBlockFormat(event: Event) {
		const value = (event.currentTarget as HTMLSelectElement).value as BlockFormat;
		blockFormat = value;
		run(() => {
			if (!editor) {
				return false;
			}
			const chain = editor.chain().focus();
			if (value === 'heading1') {
				return chain.setHeading({ level: 1 }).run();
			}
			if (value === 'heading2') {
				return chain.setHeading({ level: 2 }).run();
			}
			if (value === 'heading3') {
				return chain.setHeading({ level: 3 }).run();
			}
			if (value === 'heading4') {
				return chain.setHeading({ level: 4 }).run();
			}
			if (value === 'heading5') {
				return chain.setHeading({ level: 5 }).run();
			}
			if (value === 'heading6') {
				return chain.setHeading({ level: 6 }).run();
			}
			return chain.setParagraph().run();
		});
	}

	function setLink() {
		if (!editor) {
			return;
		}
		const previousUrl = editor.getAttributes('link').href as string | undefined;
		const url = window.prompt('링크 URL', previousUrl ?? 'https://');
		if (url === null) {
			return;
		}
		if (url.trim() === '') {
			run(() => editor?.chain().focus().extendMarkRange('link').unsetLink().run() ?? false);
			return;
		}
		run(() => editor?.chain().focus().extendMarkRange('link').setLink({ href: url.trim() }).run() ?? false);
	}

	function openImageFilePicker() {
		imageInput?.click();
	}

	function handleImageFile(event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		const file = input.files?.[0];
		input.value = '';
		if (!file || !['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 5 * 1024 * 1024) {
			return;
	}
	const objectUrl = URL.createObjectURL(file);
		const inserted = run(() => insertImageNode(objectUrl, file.name));
		if (inserted) {
			onImageFile(file, objectUrl);
		} else {
			URL.revokeObjectURL(objectUrl);
		}
	}

	function insertImageNode(src: string, alt: string) {
		if (!editor) {
			return false;
		}
		if (NodeSelectionConstructor && editor.state.selection instanceof NodeSelectionConstructor && editor.state.selection.node.type.name === 'image') {
			return editor
				.chain()
				.focus()
				.insertContentAt(editor.state.selection.to, { type: 'image', attrs: { src, alt } })
				.run();
		}
		return editor.chain().focus().setImage({ src, alt }).run();
	}
</script>

	<div class="rich-editor-shell">
	<div class="rich-editor-toolbar" aria-label="본문 서식 도구">
		<div class="rich-editor-toolbar-group" aria-label="글자 서식">
			<button type="button" aria-label="굵게" class:active={editor?.isActive('bold')} title="굵게" onclick={() => run(() => editor?.chain().focus().toggleBold().run() ?? false)}><RichEditorIcon name="bold" /></button>
			<button type="button" aria-label="기울임" class:active={editor?.isActive('italic')} title="기울임" onclick={() => run(() => editor?.chain().focus().toggleItalic().run() ?? false)}><RichEditorIcon name="italic" /></button>
			<button type="button" aria-label="밑줄" class:active={editor?.isActive('underline')} title="밑줄" onclick={() => run(() => editor?.chain().focus().toggleUnderline().run() ?? false)}><RichEditorIcon name="underline" /></button>
		</div>
		<div class="rich-editor-toolbar-group" aria-label="목록과 정렬">
			<button type="button" aria-label="번호 목록" class:active={editor?.isActive('orderedList')} title="번호 목록" onclick={() => run(() => editor?.chain().focus().toggleOrderedList().run() ?? false)}><RichEditorIcon name="ordered-list" /></button>
			<button type="button" aria-label="글머리 목록" class:active={editor?.isActive('bulletList')} title="글머리 목록" onclick={() => run(() => editor?.chain().focus().toggleBulletList().run() ?? false)}><RichEditorIcon name="bullet-list" /></button>
			<button type="button" aria-label="왼쪽 정렬" class:active={editor?.isActive({ textAlign: 'left' })} title="왼쪽 정렬" onclick={() => run(() => editor?.chain().focus().setTextAlign('left').run() ?? false)}><RichEditorIcon name="align-left" /></button>
			<button type="button" aria-label="가운데 정렬" class:active={editor?.isActive({ textAlign: 'center' })} title="가운데 정렬" onclick={() => run(() => editor?.chain().focus().setTextAlign('center').run() ?? false)}><RichEditorIcon name="align-center" /></button>
			<button type="button" aria-label="오른쪽 정렬" class:active={editor?.isActive({ textAlign: 'right' })} title="오른쪽 정렬" onclick={() => run(() => editor?.chain().focus().setTextAlign('right').run() ?? false)}><RichEditorIcon name="align-right" /></button>
		</div>
		<div class="rich-editor-toolbar-group" aria-label="문단 형식">
			<select class="rich-editor-format-select" aria-label="문단 형식" bind:value={blockFormat} onchange={setBlockFormat}>
				<option value="paragraph">Normal</option>
				<option value="heading2">H2</option>
				<option value="heading3">H3</option>
			</select>
		</div>
		<div class="rich-editor-toolbar-group" aria-label="링크와 이미지">
			<button type="button" aria-label="링크" class:active={editor?.isActive('link')} title="링크" onclick={setLink}><RichEditorIcon name="link" /></button>
			<button type="button" aria-label="이미지 파일 업로드" title="이미지 파일 업로드" onclick={openImageFilePicker}><RichEditorIcon name="upload" /></button>
			<button type="button" aria-label="되돌리기" title="되돌리기" onclick={() => run(() => editor?.chain().focus().undo().run() ?? false)}><RichEditorIcon name="undo" /></button>
			<button type="button" aria-label="다시 실행" title="다시 실행" onclick={() => run(() => editor?.chain().focus().redo().run() ?? false)}><RichEditorIcon name="redo" /></button>
		</div>
	</div>
	<input bind:this={imageInput} data-body-image-input type="file" accept="image/jpeg,image/png,image/webp" onchange={handleImageFile} hidden />
	<div bind:this={element} class="rich-editor" aria-label="프로젝트 본문 편집기"></div>
	<details class="rich-editor-preview">
		<summary>본문 미리보기</summary>
		<div class="rich-editor-preview-content">
			<ProjectRichContent html={previewHtml} allowLocalImages />
		</div>
	</details>
</div>

<style>
	.rich-editor-shell {
		display: grid;
		overflow: hidden;
		border: 1px solid var(--folio-border);
		border-radius: 8px;
		background: white;
	}

	.rich-editor-toolbar {
		display: flex;
		flex-wrap: wrap;
		gap: 8px 10px;
		align-items: center;
		padding: 8px 10px;
		border-bottom: 1px solid var(--folio-border);
		background: var(--folio-subtle);
	}

	.rich-editor-toolbar-group {
		display: inline-flex;
		flex-wrap: wrap;
		gap: 2px;
		align-items: center;
		margin-right: 0;
		padding-right: 0;
	}

	.rich-editor-toolbar-group:last-child {
		margin-right: 0;
	}

	.rich-editor-toolbar button {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		box-sizing: border-box;
		min-width: 28px;
		min-height: 24px;
		padding: 3px 5px;
		border: 0;
		border-radius: 3px;
		background: transparent;
		color: #4b5563;
		cursor: pointer;
		font-size: 12px;
		font-weight: 800;
		line-height: 1;
		transition: background-color 120ms ease, color 120ms ease;
	}

	:global(.rich-editor-toolbar .editor-icon) {
		display: block;
		width: 18px;
		height: 18px;
		flex: 0 0 18px;
	}

	.rich-editor-format-select {
		min-height: 24px;
		padding: 3px 22px 3px 5px;
		border: 0;
		border-radius: 3px;
		background: transparent;
		color: #4b5563;
		cursor: pointer;
		font-size: 12px;
		font-weight: 800;
	}

	.rich-editor-toolbar .rich-editor-format-select {
		width: 96px;
	}

	.rich-editor-toolbar button:hover,
	.rich-editor-toolbar button:focus-visible,
	.rich-editor-toolbar select:hover,
	.rich-editor-toolbar select:focus-visible,
	.rich-editor-toolbar button.active {
		background: #eaf2ff;
		color: var(--folio-blue);
	}

	.rich-editor {
		max-height: 330px;
		min-height: 240px;
		overflow-y: auto;
		padding: 14px 16px;
		color: var(--folio-navy);
		font-size: 14px;
		line-height: 1.58;
	}

	:global(.rich-editor .tiptap) {
		min-height: 210px;
		outline: none;
	}

	:global(.rich-editor .tiptap > *:first-child) {
		margin-top: 0;
	}

	:global(.rich-editor .tiptap h2) {
		margin: 18px 0 8px;
		color: var(--folio-navy);
		font-size: 18px;
		line-height: 1.35;
	}

	:global(.rich-editor .tiptap h1) {
		margin: 18px 0 8px;
		color: var(--folio-navy);
		font-size: 22px;
		line-height: 1.3;
	}

	:global(.rich-editor .tiptap h3) {
		margin: 14px 0 6px;
		font-size: 15px;
	}

	:global(.rich-editor .tiptap h4),
	:global(.rich-editor .tiptap h5),
	:global(.rich-editor .tiptap h6) {
		margin: 12px 0 5px;
	}

	:global(.rich-editor .tiptap h4) {
		font-size: 14px;
	}

	:global(.rich-editor .tiptap h5) {
		font-size: 13px;
	}

	:global(.rich-editor .tiptap h6) {
		font-size: 12px;
	}

	:global(.rich-editor .tiptap p) {
		margin: 0 0 8px;
	}

	:global(.rich-editor .tiptap ul),
	:global(.rich-editor .tiptap ol) {
		margin: 0 0 12px 22px;
		padding: 0;
	}

	:global(.rich-editor .tiptap blockquote) {
		margin: 12px 0;
		padding-left: 14px;
		border-left: 3px solid var(--folio-border);
		color: var(--folio-muted);
	}

	:global(.rich-editor .tiptap p.is-editor-empty:first-child::before) {
		float: left;
		height: 0;
		color: var(--folio-muted);
		content: attr(data-placeholder);
		pointer-events: none;
	}

	:global(.rich-editor .tiptap [data-indent='1']) {
		margin-left: 24px;
	}

	:global(.rich-editor .tiptap [data-indent='2']) {
		margin-left: 48px;
	}

	:global(.rich-editor .tiptap [data-indent='3']) {
		margin-left: 72px;
	}

	:global(.rich-editor .tiptap [data-indent='4']) {
		margin-left: 96px;
	}

	:global(.rich-editor .tiptap [data-indent='5']) {
		margin-left: 120px;
	}

	:global(.rich-editor .tiptap [data-indent='6']) {
		margin-left: 144px;
	}

	.rich-editor-toolbar button {
		box-sizing: border-box;
		min-width: 28px;
		min-height: 24px;
		padding: 3px 5px;
		font-size: 11px;
	}

	.rich-editor-toolbar-group {
		gap: 2px;
		margin-right: 0;
		padding-right: 0;
	}

	:global(.rich-editor .tiptap mark) {
		border-radius: 4px;
		background: #fff2a8;
		padding: 0 2px;
	}

	:global(.rich-editor .tiptap code) {
		border: 1px solid var(--folio-border);
		border-radius: 5px;
		background: var(--folio-subtle);
		padding: 1px 5px;
		font-size: 0.9em;
	}

	:global(.rich-editor .tiptap pre) {
		overflow-x: auto;
		margin: 12px 0;
		padding: 14px;
		border-radius: 8px;
		background: #0f172a;
		color: white;
		font-size: 13px;
		line-height: 1.55;
	}

	:global(.rich-editor .tiptap pre code) {
		border: 0;
		background: transparent;
		padding: 0;
		color: inherit;
	}

	:global(.rich-editor .tiptap a) {
		color: var(--folio-blue);
		font-weight: 800;
		text-decoration: underline;
		text-underline-offset: 3px;
	}

	:global(.rich-editor .tiptap hr) {
		margin: 22px 0;
		border: 0;
		border-top: 1px solid var(--folio-border);
	}

	:global(.rich-editor .tiptap img) {
		display: block;
		max-width: 100%;
		height: auto;
		margin: 12px 0;
		border-radius: 8px;
	}

	:global(.rich-editor .tiptap [data-type='inline-math']) {
		display: inline-block;
		max-width: 100%;
		overflow-x: auto;
		vertical-align: middle;
	}

	:global(.rich-editor .tiptap [data-type='block-math']) {
		max-width: 100%;
		overflow-x: auto;
		padding: 8px 0;
	}

	@media (max-width: 760px) {
		.rich-editor-toolbar {
			gap: 0;
		}

		.rich-editor-toolbar-group {
			width: 100%;
			margin-right: 0;
			padding-right: 0;
			border-right: 0;
		}

		.rich-editor-toolbar button {
			flex: 0 0 auto;
		}

		.rich-editor {
			min-height: 380px;
			padding: 15px;
		}
	}

	.rich-editor-preview {
		border-top: 1px solid var(--folio-border);
		background: #f8fbff;
	}

	.rich-editor-preview summary {
		display: flex;
		align-items: center;
		min-height: 42px;
		padding: 0 16px;
		color: var(--folio-blue);
		cursor: pointer;
		font-size: 13px;
		font-weight: 800;
	}

	.rich-editor-preview-content {
		display: grid;
		gap: 10px;
		padding: 14px 18px 18px;
		border-top: 1px solid rgba(201, 216, 238, 0.68);
		color: var(--folio-navy);
		font-size: 14px;
		line-height: 1.65;
	}

	:global(.rich-editor-preview-content h2) {
		margin: 8px 0 0;
		font-size: 17px;
		line-height: 1.35;
	}

	:global(.rich-editor-preview-content h1) {
		margin: 8px 0 0;
		font-size: 20px;
		line-height: 1.3;
	}

	:global(.rich-editor-preview-content h3) {
		margin: 6px 0 0;
		font-size: 15px;
	}

	:global(.rich-editor-preview-content h4),
	:global(.rich-editor-preview-content h5),
	:global(.rich-editor-preview-content h6) {
		margin: 6px 0 0;
	}

	:global(.rich-editor-preview-content p),
	:global(.rich-editor-preview-content ul),
	:global(.rich-editor-preview-content ol),
	:global(.rich-editor-preview-content blockquote),
	:global(.rich-editor-preview-content pre) {
		margin: 0;
	}
</style>
