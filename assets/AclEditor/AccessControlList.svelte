<script>
    import { createEventDispatcher, onMount } from "svelte";
    const dispatch = createEventDispatcher();


    export let acl = {
        id: -1,
        list_id: -1,
        type: "MISSING_TYPE",
        label: "MISSING_LABEL",
        params: "MISSING_PARAMS",
        isFile: false,
        fileId: -1,
        priority: -100
    };
    export let types = [];
    export let files = [];

    let helpString = "";
    let busy = false;

    let handleHelpString = function() {
        helpString = types.find((val) => val.internalName == acl.type).friendlyName;
    };

    
    onMount(() => {        
        if (acl.type != "ACL_TYPE_NO_TYPE") {
            handleHelpString();
        }
    });
    
    let handleSave = async function () {
        busy = true;
        let result = await fetch("/api/v1/acl/update", {
            method: "POST",
            body: JSON.stringify(acl),
            headers: {
                "Content-Type": "application/json",
            }

        }).then((res) => res.json());

        if (result.status == "ok") {
            acl.id = result.response[0].id;
            console.log(result);
        }

        busy = false;
    };

    let handleDelete = async function () {
        busy = true;
        if (acl.id != -1) {
            let result = await fetch("/api/v1/acl/delete", {
                method: "POST",
                body: JSON.stringify(acl),
                headers: {
                    "Content-Type": "application/json",
                }
            }).then((res) => res.json());
        }
        dispatch("deleted", { list_id: acl.list_id });
        busy = false;
    };
</script>
<div class="container-fluid rounded border mb-2">
    <div class="row p-2">
        <div class="col">
                <label for="acl_label_{acl.list_id}" class="form-label">ACL Label</label>
                <input type="text" name="" id="acl_label_{acl.list_id}" class="form-control" bind:value={acl.label}/>
        </div>
        <div class="col">
                <label for="acl_type_{acl.list_id}" class="form-label">Type</label>
                <select name="" id="acl_type_{acl.list_id}" class="form-select" bind:value={acl.type}>
                    <option value="ACL_TYPE_NO_TYPE">Select ACL Type</option>
                    {#each types as type}
                        <option value="{type.internalName}">{type.configName}</option>
                    {/each}
                </select>
        </div>
        <div class="col">
            <label for="acl_type_{acl.list_id}" class="form-label">{acl.isFile ? "File" : "Parameters"}</label>
            <div class="input-group">
                <div class="input-group-text">
                    <input type="checkbox" name="" id="acl_file_check_{acl.list_id}" class="form-check-input mt-0" bind:checked={acl.isFile} data-bs-toggle="tooltip" data-bs-placement="top" title="File"/>
                </div>
                {#if acl.isFile}
                <select name="" id="acl_file_select_{acl.list_id}" class="form-select" bind:value={acl.fileId}>
                    <option value="-1">Select assoc. file</option>
                    {#each files as file}
                        <option value="{file.id}">{file.label}</option>
                    {/each}
                </select>
                {:else}
                <input type="text" class="form-control" bind:value={acl.params}>
                {/if}
            </div>
        </div>
        <div class="col">
            <label for="acl_priority_{acl.list_id}" class="form-label">Priority</label>
            <input type="number" name="" id="acl_priority_{acl.list_id}" bind:value={acl.priority} class="form-control">
        </div>
        <div class="col align-self-end text-center">
            {#if acl.id == -1}
                <button name="" id="acl_save_{acl.list_id}" class="btn btn-primary" on:click={handleSave} disabled={busy}>
                    Save
                </button>
                <button name="" id="acl_clear_{acl.list_id}" class="btn btn-danger" on:click={handleDelete} disabled={busy}>
                    Delete
                </button>
            {:else}
                <button name="" id="acl_update_{acl.list_id}" class="btn btn-success" on:click={handleSave} disabled={busy}>
                    Update
                </button>
                <button name="" id="acl_delete_{acl.list_id}" class="btn btn-danger" on:click={handleDelete} disabled={busy}>
                    Delete
                </button>
            {/if}
        </div>
    </div>
    {#if helpString.length > 0}
    <div class="row">
        <p class="alert alert-light">
            {helpString}
        </p>
    </div>
    {/if}
</div>