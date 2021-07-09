<script>
    import { createEventDispatcher, onMount } from "svelte";
    const dispatch = createEventDispatcher();

    export let directive = {
        id: -1,
        deny: false,
        list_id: -1,
        acls: [],
        priority: -100,
    };

    let aclListId = 0;
    let currentTypeHint = "";
    let exampleAcl = {
        id: -1,
        acldir_id: -1,
        negated: false,
    };

    export let acls = [];
    export let types = [];

    let busy = false;

    onMount(() => {
        if (directive.acls.length > 0) {
            directive.acls = directive.acls.map((val) => {
                val["list_id"] = aclListId++;
                return val;
            })
        }
        
        if (directive.type != "DIR_TYPE_NO_TYPE") {
            handleSelectChange();
        }
    });

    let handleSelectChange = async function() {
        currentTypeHint = types.find((val) => val.internalName == directive.type).friendlyName;
        console.log(currentTypeHint);
    };

    let handleNewAcl = async function() {
        let newAcl = Object.assign({}, exampleAcl);
        newAcl["list_id"] = aclListId++;
        directive.acls.push(newAcl);
        directive.acls = directive.acls;
    };


    let handleSave = async function () {
        busy = true;
        let result = await fetch("/api/v1/directive/update", {
            method: "POST",
            body: JSON.stringify(directive),
            headers: {
                "Content-Type": "application/json",
            },
        }).then((res) => res.json());

        if (result.status == "ok") {
            directive = result.response[0]
            console.log(result);
        }
        busy = false;
    };

    let handleDelete = async function () {
        busy = true;
        if (directive.id != -1) {
            let result = await fetch("/api/v1/directive/delete", {
                method: "POST",
                body: JSON.stringify(directive),
                headers: {
                    "Content-Type": "application/json",
                },
            }).then((res) => res.json());
        }
        dispatch("deleted", { list_id: directive.list_id });
        busy = false;
    };

    $: console.log(directive);
</script>

<div class="container-fluid rounded border mb-2">
    <div class="row p-2">
        <div class="col">
            <label for="dir_type_{directive.list_id}" class="form-label">Type</label
            >
            <!-- svelte-ignore a11y-no-onchange -->
            <select
                name=""
                id="dir_type_{directive.list_id}"
                class="form-select"
                bind:value={directive.type}
                on:change={handleSelectChange}
            >
                <option value="DIR_TYPE_NO_TYPE">Select Directive Type</option>
                {#each types as type}
                    <option value={type.internalName}
                        >{type.configName}</option
                    >
                {/each}
            </select>    
        </div>
        <div class="col-1">
            <label class="form-check-label" for="dir_radio_allow_{directive.list_id}">
                Rule
            </label>
            <div class="form-check">
                <input
                    class="form-check-input"
                    type="radio"
                    name=""
                    id="dir_radio_allow_{directive.list_id}"
                    bind:group={directive.deny}
                    value={false}
                />
                <label class="form-check-label" for="dir_radio_allow_{directive.list_id}">
                    ALLOW
                </label>
            </div>
            <div class="form-check">
                <input
                    class="form-check-input"
                    type="radio"
                    name=""
                    id="dir_radio_deny_{directive.list_id}"
                    bind:group={directive.deny}
                    value={true}
                />
                <label class="form-check-label" for="dir_radio_deny_{directive.list_id}">
                    DENY
                </label>
            </div>
        </div>
        <div class="col border rounded p-1">
            <button class="btn btn-sm btn-success" on:click={handleNewAcl}>+</button>
            <label for="dir_acls{directive.list_id}" class="form-label"
                >ACLs</label
            >
            <div class="container-fluid">
                {#each directive.acls as acl (acl.list_id)}
                    <div class="row mb-1">
                        <div class="col-3 form-switch form-check ">
                            <input type="checkbox" name="" id="dir_acl_check_{acl.list_id}" class="form-check-input" bind:checked={acl.negated}>
                            <label for="dir_acl_check_{acl.list_id}" class="form-check-label">Negate</label>
                        </div>
                        <div class="col">
                            <select name="" id="dir_acl_select_{acl.list_id}" class="form-select" bind:value={acl.id}>
                                <option value="-1">Select ACL</option>
                                {#each acls as possibleAcl (possibleAcl.id)}
                                    <option value="{possibleAcl.id}">{possibleAcl.label}</option>
                                {/each}
                            </select>
                        </div>
                    </div>
                {/each}
            </div>
        </div>
        <div class="col-1">
            <label for="dir_priority{directive.list_id}" class="form-label"
                >Priority</label
            >
            <input
                type="number"
                name=""
                id="dir_priority{directive.list_id}"
                bind:value={directive.priority}
                class="form-control"
            />
        </div>
        <div class="col-1 align-self-center text-center">
            {#if directive.id == -1}
                <div class="mb-1">
                    <button
                        name=""
                        id="dir_save_{directive.list_id}"
                        class="btn btn-primary"
                        on:click={handleSave}
                        disabled={busy}
                    >
                        Save
                    </button>
                </div>
                <div>
                    <button
                        name=""
                        id="dir_clear_{directive.list_id}"
                        class="btn btn-danger"
                        on:click={handleDelete}
                        disabled={busy}
                    >
                        Delete
                    </button>
                </div>
            {:else}
                <div class="mb-1">
                    <button
                        name=""
                        id="dir_update_{directive.list_id}"
                        class="btn btn-success"
                        on:click={handleSave}
                        disabled={busy}
                    >
                        Update
                    </button>
                </div>
                <div>
                    <button
                        name=""
                        id="dir_delete_{directive.list_id}"
                        class="btn btn-danger"
                        on:click={handleDelete}
                        disabled={busy}
                    >
                        Delete
                    </button>
                </div>
            {/if}
        </div>
    </div>
    
    <div class="row">
        {#if currentTypeHint.length > 0}
        <div class="alert alert-light" role="alert">
            {currentTypeHint}
        </div>
        {/if}
    </div>
</div>
