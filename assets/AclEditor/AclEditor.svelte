<script>
    import { onMount } from 'svelte';
    import AccessControlList from './AccessControlList.svelte';
    
    export let aclTypes = {};
    let acls = [];
    let files = [];

    let list_id = 0;

    let aclPlaceholder = {
        "id": -1,
        "label": "Unnamed ACL",
        "type": "ACL_TYPE_NO_TYPE",
        "isFile": false,
        "fileId": -1,
        "params": "",
        "priority": 100
    };

    let handleNew = function() {
        let newAcl = Object.assign({}, aclPlaceholder);
        newAcl["list_id"] = list_id++;
        acls.push(newAcl);
        acls = acls;
    };

    let filesPromise = fetch("/api/v1/files/get_all").then((res) => {
        if (res.status >= 200 && res.status < 300) {
            return res.json();
        }
    }).then((res) => {
        if (res.status === "ok") {
            files = res.response
        }
    });

    let aclsPromise = fetch("/api/v1/acl/get_all").then((res) => {
        if (res.status >= 200 && res.status < 300) {
            return res.json();
        }
    }).then((res) => {
        if (res.status === "ok") {
            acls = res.response.map((val) => {
                val["list_id"] = list_id++;
                return val;
            })
        }
    });

    let allPromise = Promise.all([aclsPromise, filesPromise]);
    

    let onDelete = function(ev) {
        acls = acls.filter(val => val.list_id != ev.detail.list_id);
    };

    $: console.log(acls);
</script>

<div class="container-fluid p-3">
    {#await allPromise}
        Loading...
    {:then}
        <div class="row mb-3">
            <div class="col-1 form-group">
                <label for="button_add_new_acl" class="form-label"></label>
                <button id="button_add_new_acl" class="form-control btn btn-success" on:click={handleNew}>Create</button>
            </div>
        </div>
        {#each acls as acl (acl.list_id) }
            <AccessControlList types={aclTypes} {files} bind:acl={acl} on:deleted={onDelete}/>
        {/each}
    {/await}
</div>