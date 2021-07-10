<script>
    import { onMount } from 'svelte';
    import AccessDirective from './AccessDirective.svelte';
    
    export let directiveTypes = {};
    let directives = [];
    let acls = [];

    let list_id = 0;

    let directivePlaceholder = {
        "id": -1,
        "deny": false,
        "type": "DIR_TYPE_NO_TYPE",
        "priority": 100
    };

    let handleNew = function() {
        let newDirective = Object.assign({}, directivePlaceholder);
        newDirective["list_id"] = list_id++;
        newDirective["acls"] = [];
        directives.push(newDirective);
        directives = directives;
    };

    let directivesPromise = fetch("/api/v1/directive/get_all").then((res) => {
        if (res.status >= 200 && res.status < 300) {
            return res.json();
        }
    }).then((res) => {
        if (res.status === "ok") {
            directives = res.response.map((val) => {
                val["list_id"] = list_id++;
                return val;
            })
        }
    });

    let aclPromise = fetch("/api/v1/acl/get_all").then((res) => {
        if (res.status >= 200 && res.status < 300) {
            return res.json();
        }
    }).then((res) => {
        if (res.status === "ok") {
            acls = res.response;
        }
    });

    let allPromise = Promise.all([directivesPromise, aclPromise]);
    

    let onDelete = function(ev) {
        directives = directives.filter(val => val.list_id != ev.detail.list_id);
    };

</script>

<div class="container-fluid p-3">
    
    <div class="row text-center">
        <h1>Access Directives</h1>
    </div>
    {#await allPromise}
        Loading...
    {:then}
        <div class="row mb-3">
            <div class="form-group text-center">
                <button id="button_add_new_directive" class="form-control btn btn-success" on:click={handleNew}>Create</button>
            </div>
        </div>
        {#each directives as directive (directive.list_id)}
            <AccessDirective types={directiveTypes} {acls} bind:directive={directive} on:deleted={onDelete}/>
        {/each}
    {/await}
</div>