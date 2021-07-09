import DirectiveEditor from "./DirectiveEditor.svelte";

const app = new DirectiveEditor({
    target: document.querySelector("div#directive-editor"),
    props: {
        directiveTypes: directive_types
    }
});