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
	let fontSize = $state('default');
	let textColor = $state('default');
	let highlightColor = $state('default');
	let fontFamily = $state('default');
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
		const color = instance.getAttributes('textStyle').color as string | undefined;
		textColor = normalizeTextColor(color);
		const family = instance.getAttributes('textStyle').fontFamily as string | undefined;
		fontFamily = normalizeFontFamily(family);
		const size = instance.getAttributes('textStyle').fontSize as string | undefined;
		fontSize = normalizeFontSize(size);
		const highlight = instance.getAttributes('highlight').color as string | undefined;
		highlightColor = normalizeHighlightColor(highlight);
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

	function setFontSize(event: Event) {
		const value = (event.currentTarget as HTMLSelectElement).value;
		fontSize = value;
		run(() =>
			value === 'default'
				? (editor?.chain().focus().unsetFontSize().run() ?? false)
				: (editor?.chain().focus().setFontSize(value).run() ?? false)
		);
	}

	function changeIndent(delta: number) {
		if (!editor) {
			return;
		}
		const { state } = editor;
		const transaction = state.tr;
		const targets: Array<{ node: typeof state.doc; position: number }> = [];
		const blockTypes = new Set(['paragraph', 'heading']);
		if (state.selection.empty) {
			for (let depth = state.selection.$from.depth; depth > 0; depth -= 1) {
				const node = state.selection.$from.node(depth);
				if (blockTypes.has(node.type.name)) {
					targets.push({ node: node as typeof state.doc, position: state.selection.$from.before(depth) });
					break;
				}
			}
		} else {
			state.doc.nodesBetween(state.selection.from, state.selection.to, (node, position) => {
				if (blockTypes.has(node.type.name)) {
					targets.push({ node: node as typeof state.doc, position });
				}
			});
		}
		let changed = false;
		for (const { node, position } of targets) {
			const indent = Math.max(0, Math.min(6, (Number(node.attrs.indent) || 0) + delta));
			transaction.setNodeMarkup(position, undefined, { ...node.attrs, indent });
			changed = true;
		}
		if (changed) {
			editor.view.dispatch(transaction);
			editor.commands.focus();
		}
	}

	function setTextColor(event: Event) {
		const value = (event.currentTarget as HTMLSelectElement).value;
		textColor = value;
		run(() =>
			value === 'default'
				? (editor?.chain().focus().unsetColor().run() ?? false)
				: (editor?.chain().focus().setColor(value).run() ?? false)
		);
	}

	function setHighlightColor(event: Event) {
		const value = (event.currentTarget as HTMLSelectElement).value;
		highlightColor = value;
		run(() =>
			value === 'default'
				? (editor?.chain().focus().unsetHighlight().run() ?? false)
				: (editor?.chain().focus().toggleHighlight({ color: value }).run() ?? false)
		);
	}

	function setFontFamily(event: Event) {
		const value = (event.currentTarget as HTMLSelectElement).value;
		fontFamily = value;
		run(() =>
			value === 'default'
				? (editor?.chain().focus().unsetFontFamily().run() ?? false)
				: (editor?.chain().focus().setFontFamily(value).run() ?? false)
		);
	}

	function normalizeTextColor(value: string | undefined) {
		const normalized = value?.replace(/\s+/g, '').toLowerCase();
		if (normalized === '#8a98ad' || normalized === 'rgb(138,152,173)') {
			return '#8a98ad';
		}
		if (normalized === '#1459c8' || normalized === 'rgb(20,89,200)') {
			return '#1459c8';
		}
		if (normalized === '#c81438' || normalized === 'rgb(200,20,56)') {
			return '#c81438';
		}
		return 'default';
	}

	function normalizeHighlightColor(value: string | undefined) {
		const normalized = value?.replace(/\s+/g, '').toLowerCase();
		if (normalized === '#fff2a8' || normalized === 'rgb(255,242,168)') {
			return '#fff2a8';
		}
		if (normalized === '#d8f3dc' || normalized === 'rgb(216,243,220)') {
			return '#d8f3dc';
		}
		if (normalized === '#dbeafe' || normalized === 'rgb(219,234,254)') {
			return '#dbeafe';
		}
		return 'default';
	}

	function normalizeFontFamily(value: string | undefined) {
		const normalized = value?.replace(/["']/g, '').trim().toLowerCase();
		return normalized === 'serif' || normalized === 'monospace' || normalized === 'sans-serif' ? normalized : 'default';
	}

	function normalizeFontSize(value: string | undefined) {
		const normalized = value?.trim().toLowerCase();
		return normalized === '0.75em' || normalized === '1.5em' || normalized === '2.5em' ? normalized : 'default';
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

	function insertImage() {
		if (!editor) {
			return;
		}
		const url = window.prompt('이미지 URL', 'https://');
		if (url === null || !/^https?:\/\/[^\s]+$/i.test(url.trim())) {
			return;
		}
		const alt = window.prompt('이미지 설명', '') ?? '';
		run(() => insertImageNode(url.trim(), alt.trim()));
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

	function insertFormula() {
		if (!editor) {
			return;
		}
		const latex = window.prompt('수식 입력 (LaTeX)', 'x^2 + y^2 = z^2');
		if (latex === null || !latex.trim()) {
			return;
		}
		run(() => editor?.chain().focus().insertInlineMath({ latex: latex.trim() }).run() ?? false);
	}
</script>

	<div class="rich-editor-shell">
	<div class="rich-editor-toolbar" aria-label="본문 서식 도구">
		<div class="rich-editor-toolbar-group" aria-label="글자 서식">
			<button type="button" aria-label="굵게" class:active={editor?.isActive('bold')} title="굵게" onclick={() => run(() => editor?.chain().focus().toggleBold().run() ?? false)}><RichEditorIcon name="bold" /></button>
			<button type="button" aria-label="기울임" class:active={editor?.isActive('italic')} title="기울임" onclick={() => run(() => editor?.chain().focus().toggleItalic().run() ?? false)}><RichEditorIcon name="italic" /></button>
			<button type="button" aria-label="밑줄" class:active={editor?.isActive('underline')} title="밑줄" onclick={() => run(() => editor?.chain().focus().toggleUnderline().run() ?? false)}><RichEditorIcon name="underline" /></button>
			<button type="button" aria-label="취소선" class:active={editor?.isActive('strike')} title="취소선" onclick={() => run(() => editor?.chain().focus().toggleStrike().run() ?? false)}><RichEditorIcon name="strike" /></button>
			<button type="button" aria-label="아래첨자" class:active={editor?.isActive('subscript')} title="아래첨자" onclick={() => run(() => editor?.chain().focus().toggleSubscript().run() ?? false)}><RichEditorIcon name="subscript" /></button>
			<button type="button" aria-label="위첨자" class:active={editor?.isActive('superscript')} title="위첨자" onclick={() => run(() => editor?.chain().focus().toggleSuperscript().run() ?? false)}><RichEditorIcon name="superscript" /></button>
		</div>
		<div class="rich-editor-toolbar-group" aria-label="색상">
			<select class="rich-editor-highlight-select" aria-label="배경 색상" bind:value={highlightColor} onchange={setHighlightColor}>
				<option value="default">배경 없음</option>
				<option value="#fff2a8">형광 노랑</option>
				<option value="#d8f3dc">형광 초록</option>
				<option value="#dbeafe">형광 파랑</option>
			</select>
			<select class="rich-editor-color-select" aria-label="글자 색상" bind:value={textColor} onchange={setTextColor}>
				<option value="default">A</option>
				<option value="#8a98ad">A 회색</option>
				<option value="#1459c8">A 파랑</option>
				<option value="#c81438">A 빨강</option>
			</select>
		</div>
		<div class="rich-editor-toolbar-group" aria-label="목록과 정렬">
			<button type="button" aria-label="번호 목록" class:active={editor?.isActive('orderedList')} title="번호 목록" onclick={() => run(() => editor?.chain().focus().toggleOrderedList().run() ?? false)}><RichEditorIcon name="ordered-list" /></button>
			<button type="button" aria-label="글머리 목록" class:active={editor?.isActive('bulletList')} title="글머리 목록" onclick={() => run(() => editor?.chain().focus().toggleBulletList().run() ?? false)}><RichEditorIcon name="bullet-list" /></button>
			<button type="button" aria-label="내어쓰기" title="내어쓰기" onclick={() => changeIndent(-1)}><RichEditorIcon name="outdent" /></button>
			<button type="button" aria-label="들여쓰기" title="들여쓰기" onclick={() => changeIndent(1)}><RichEditorIcon name="indent" /></button>
			<button type="button" aria-label="왼쪽 정렬" class:active={editor?.isActive({ textAlign: 'left' })} title="왼쪽 정렬" onclick={() => run(() => editor?.chain().focus().setTextAlign('left').run() ?? false)}><RichEditorIcon name="align-left" /></button>
			<button type="button" aria-label="가운데 정렬" class:active={editor?.isActive({ textAlign: 'center' })} title="가운데 정렬" onclick={() => run(() => editor?.chain().focus().setTextAlign('center').run() ?? false)}><RichEditorIcon name="align-center" /></button>
			<button type="button" aria-label="오른쪽 정렬" class:active={editor?.isActive({ textAlign: 'right' })} title="오른쪽 정렬" onclick={() => run(() => editor?.chain().focus().setTextAlign('right').run() ?? false)}><RichEditorIcon name="align-right" /></button>
		</div>
		<div class="rich-editor-toolbar-group" aria-label="문단 형식과 크기">
			<select class="rich-editor-format-select" aria-label="문단 형식" bind:value={blockFormat} onchange={setBlockFormat}>
				<option value="paragraph">Normal</option>
				<option value="heading1">H1</option>
				<option value="heading2">H2</option>
				<option value="heading3">H3</option>
				<option value="heading4">H4</option>
				<option value="heading5">H5</option>
				<option value="heading6">H6</option>
			</select>
			<select class="rich-editor-size-select" aria-label="글자 크기" bind:value={fontSize} onchange={setFontSize}>
				<option value="default">Normal</option>
				<option value="0.75em">Small</option>
				<option value="1.5em">Large</option>
				<option value="2.5em">Huge</option>
			</select>
		</div>
		<div class="rich-editor-toolbar-group" aria-label="고급 블록 서식">
			<button type="button" aria-label="수식 삽입" title="수식 삽입" onclick={insertFormula}><RichEditorIcon name="formula" /></button>
			<button type="button" aria-label="인용" class:active={editor?.isActive('blockquote')} title="인용" onclick={() => run(() => editor?.chain().focus().toggleBlockquote().run() ?? false)}><RichEditorIcon name="blockquote" /></button>
			<button type="button" aria-label="인라인 코드" class:active={editor?.isActive('code')} title="인라인 코드" onclick={() => run(() => editor?.chain().focus().toggleCode().run() ?? false)}><RichEditorIcon name="code" /></button>
			<button type="button" aria-label="코드 블록" class:active={editor?.isActive('codeBlock')} title="코드 블록" onclick={() => run(() => editor?.chain().focus().toggleCodeBlock().run() ?? false)}><RichEditorIcon name="code-block" /></button>
			<button type="button" aria-label="구분선" title="구분선" onclick={() => run(() => editor?.chain().focus().setHorizontalRule().run() ?? false)}><RichEditorIcon name="rule" /></button>
			<button type="button" aria-label="서식 지우기" title="서식 지우기" onclick={() => run(() => editor?.chain().focus().unsetAllMarks().clearNodes().run() ?? false)}><RichEditorIcon name="clear" /></button>
		</div>
		<div class="rich-editor-toolbar-group" aria-label="링크와 이미지">
			<button type="button" aria-label="링크" class:active={editor?.isActive('link')} title="링크" onclick={setLink}><RichEditorIcon name="link" /></button>
			<button type="button" aria-label="이미지 삽입" title="이미지 삽입" onclick={insertImage}><RichEditorIcon name="image" /></button>
			<button type="button" aria-label="이미지 파일 업로드" title="이미지 파일 업로드" onclick={openImageFilePicker}><RichEditorIcon name="upload" /></button>
			<button type="button" aria-label="링크 해제" title="링크 해제" onclick={() => run(() => editor?.chain().focus().unsetLink().run() ?? false)}><RichEditorIcon name="unlink" /></button>
			<button type="button" aria-label="되돌리기" title="되돌리기" onclick={() => run(() => editor?.chain().focus().undo().run() ?? false)}><RichEditorIcon name="undo" /></button>
			<button type="button" aria-label="다시 실행" title="다시 실행" onclick={() => run(() => editor?.chain().focus().redo().run() ?? false)}><RichEditorIcon name="redo" /></button>
		</div>
		<div class="rich-editor-toolbar-group" aria-label="글꼴">
			<select class="rich-editor-font-select" aria-label="글꼴" bind:value={fontFamily} onchange={setFontFamily}>
				<option value="default">Sans Serif</option>
				<option value="serif">Serif</option>
				<option value="monospace">Monospace</option>
			</select>
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
		gap: 0;
		padding: 8px;
		border-bottom: 1px solid var(--folio-border);
		background: var(--folio-subtle);
	}

	.rich-editor-toolbar-group {
		display: inline-flex;
		flex-wrap: wrap;
		gap: 0;
		align-items: center;
		margin-right: 12px;
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

	.rich-editor-color-select {
		min-height: 28px;
		padding: 0 24px 0 8px;
		border: 1px solid var(--folio-border);
		border-radius: 8px;
		background: white;
		color: var(--folio-navy);
		cursor: pointer;
		font-size: 12px;
		font-weight: 800;
	}

	.rich-editor-toolbar .rich-editor-format-select {
		width: 82px;
	}

	.rich-editor-toolbar .rich-editor-color-select {
		width: 72px;
	}

	.rich-editor-toolbar .rich-editor-highlight-select {
		width: 88px;
	}

	.rich-editor-toolbar .rich-editor-font-select {
		width: 96px;
	}

	.rich-editor-toolbar .rich-editor-size-select {
		width: 82px;
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

	.rich-editor-toolbar {
		gap: 0;
		align-items: center;
	}

	.rich-editor-toolbar button {
		box-sizing: border-box;
		min-width: 28px;
		min-height: 24px;
		padding: 3px 5px;
		font-size: 11px;
	}

	.rich-editor-toolbar-group {
		gap: 0;
		margin-right: 8px;
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
