<script>
    import Browser from "./Browser.svelte";
    import { Loading } from "carbon-components-svelte";
    let p2r_url = "permission2role.json";
    let r2p_url = "role2permission.json";


    async function dataFetcher() {
        const p2r = fetch(p2r_url).then((response) => response.json());
        const r2p = fetch(r2p_url).then((response) => response.json());
        return await Promise.all([p2r, r2p]);
    }

    let dataFetch = dataFetcher();
    
</script>


<div id="wrapper">
    <h1>Google Cloud IAM role search</h1>
    {#await dataFetch}
    <Loading />
    {:then [p2r, r2p]}
    <Browser p2r={p2r} r2p={r2p} />
    {:catch error}
    <p>{error.message}</p>
    {/await}
</div>



<style lang="scss" global>
  @import "carbon-components-svelte/css/all";
  #wrapper {
      margin: 10px;
  }
</style>
