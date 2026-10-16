import React, { useEffect, useRef } from 'react';
import { EditorState } from '@codemirror/state';
import { EditorView, keymap, lineNumbers, highlightActiveLineGutter, highlightSpecialChars, drawSelection, dropCursor } from '@codemirror/view';
import { defaultKeymap, indentWithTab, history, historyKeymap } from '@codemirror/commands';
import { python } from '@codemirror/lang-python';
import { oneDark } from '@codemirror/theme-one-dark';
import { syntaxHighlighting, defaultHighlightStyle, bracketMatching } from '@codemirror/language';

export default function CodeEditor({ value, onChange, onRun, disabled = false }) {
  const editorRef = useRef(null);
  const viewRef = useRef(null);
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;

  useEffect(() => {
    if (!editorRef.current) return;

    const updateListener = EditorView.updateListener.of((update) => {
      if (update.docChanged && onChangeRef.current) {
        const doc = update.state.doc.toString();
        onChangeRef.current(doc);
      }
    });

    const runKeymap = keymap.of([
      {
        key: 'Mod-Enter',
        run: () => {
          if (onRun) onRun();
          return true;
        },
      },
    ]);

    const state = EditorState.create({
      doc: value || '',
      extensions: [
        lineNumbers(),
        highlightActiveLineGutter(),
        highlightSpecialChars(),
        history(),
        drawSelection(),
        dropCursor(),
        bracketMatching(),
        syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
        python(),
        oneDark,
        keymap.of([...defaultKeymap, ...historyKeymap, indentWithTab]),
        runKeymap,
        updateListener,
        EditorView.editable.of(!disabled),
        EditorView.theme({
          '&': {
            height: '100%',
            fontSize: '14px',
            fontFamily: '"Fira Code", monospace, Consolas',
            backgroundColor: '#0d1117',
          },
          '.cm-scroller': { overflow: 'auto' },
          '.cm-content': { padding: '12px 0' },
          '.cm-line': { padding: '0 12px' },
          '&.cm-focused': { outline: 'none' },
        }),
      ],
    });

    const view = new EditorView({
      state,
      parent: editorRef.current,
    });

    viewRef.current = view;

    return () => {
      view.destroy();
    };
  }, []);

  // Sync external value changes (e.g. Reset or Switching challenge)
  useEffect(() => {
    if (viewRef.current) {
      const currentDoc = viewRef.current.state.doc.toString();
      if (value !== currentDoc) {
        viewRef.current.dispatch({
          changes: { from: 0, to: currentDoc.length, insert: value || '' },
        });
      }
    }
  }, [value]);

  return (
    <div
      ref={editorRef}
      className="code-editor-container"
      style={{
        height: '100%',
        minHeight: '360px',
        width: '100%',
        borderRadius: '8px',
        overflow: 'hidden',
        border: '1px solid #30363d',
      }}
    />
  );
}
