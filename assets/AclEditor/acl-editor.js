import AclEditor from "./AclEditor.svelte";

const app = new AclEditor({
    target: document.querySelector("div#acl-editor"),
    props: {
        aclTypes: acl_types
    }
});