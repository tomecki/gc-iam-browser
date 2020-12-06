<script>
  import {
    Grid,
    Row,
    Column,
    Search,
    MultiSelect,
    Tag,
    Form
  } from "carbon-components-svelte";

  import { DataTable, Button } from "carbon-components-svelte";
  import Add16 from "carbon-icons-svelte/lib/Add16";
  import TrashCan16 from "carbon-icons-svelte/lib/TrashCan16";

  export let p2r;
  export let r2p;
  let filtered_namespaces = [];
  let filtered_areas_ids = [];
  let permission_selector_row_ids = [];
  let suggested_roles = [];
  let selected_permissions = [];
  let permission_subset_rows = [];

  Set.prototype.difference = function(setB) {
    var difference = new Set(this);
    for (var elem of setB) {
      difference.delete(elem);
    }
    return difference;
  };

  Set.prototype.union = function(setB) {
    var union = new Set(this);
    for (var elem of setB) {
      union.add(elem);
    }
    return union;
  };
  const namespace_matches = function(key, selection) {
    for (const selected of selection) {
      if (key.startsWith(unique_namespaces[selected].text)) {
        return true;
      }
    }
    return false;
  };
  const get_unique_namespaces = function(p2r) {
    const unique_namespaces = [
      ...new Set(Object.keys(p2r).map(key => key.split(".")[0]))
    ];
    let i = 0;
    return unique_namespaces.map(x => ({ text: x, id: i++ }));
  };
  const get_all_unique_areas = function(p2r) {
    const unique_areas = [
      ...new Set(
        Object.keys(p2r).map(key => {
          let split_arr = key.split(".");
          return `${split_arr[0]}.${split_arr[1]}`;
        })
      )
    ];
    let i = 0;
    return unique_areas.map(x => ({ text: x, id: i++ }));
  };
  const get_unique_areas = function(list, filtered_namespaces) {
    return list.filter(x => namespace_matches(x.text, filtered_namespaces));
  };

  const subset_permissions = function(filtered_areas) {
    return Object.keys(p2r).filter(x =>
      filtered_areas.some(y => x.startsWith(y))
    );
  };
  const is_selected_permission = function(permission, selected_permissions) {
    return permission in selected_permissions;
  };

  const all_unique_areas = get_all_unique_areas(p2r);
  const unique_namespaces = get_unique_namespaces(p2r);

  const permission_selector_header = [
    { key: "id", value: "Permission" },
    { key: "action", value: "Action" }
  ];

  $: unique_areas = get_unique_areas(all_unique_areas, filtered_namespaces);
  $: filtered_areas = filtered_areas_ids.map(x => all_unique_areas[x].text);
  $: filtered_permissions = subset_permissions(filtered_areas);

  $: permission_selector_rows = filtered_permissions.map(x => ({
    id: x,
    action: x
  }));
  const add_permission = function(permission) {
    if (!selected_permissions.includes(permission)) {
      selected_permissions = [...selected_permissions, permission].sort();
    }
  };
  const remove_permission = function(permission) {
    selected_permissions = selected_permissions.filter(x => x !== permission);
  };
  $: permission_subset_rows = selected_permissions.map(x => ({
    id: x,
    action: x
  }));

  const role_suggestion_heuristic = function(selected_permissions, r2p) {
    const selected_permissions_set = new Set(selected_permissions);
    let candidate_roles = Object.keys(r2p)
      .filter(role =>
        r2p[role].some(permission => selected_permissions_set.has(permission))
      )
      .sort((a, b) => r2p[a] - r2p[b]);
    console.log(candidate_roles.slice(0, 20));
    let empty_solution = {
      remaining: selected_permissions_set,
      roles: new Set(),
      permissions_granted: new Set()
    };
    let solution_space = new Set([empty_solution]);
    let unique_result_role_sets = new Set();
    let result = [];
    let steps = 0;
    while (solution_space.size > 0) {
      let new_solution_space = new Set();
      for (let solution of solution_space) {
        for (let role of candidate_roles) {
          for (let permission of [...solution.remaining].sort()) {
            if (!solution.roles.has(role) && r2p[role].includes(permission)) {
              let new_solution = {
                permissions_granted: solution.permissions_granted.union(
                  new Set(r2p[role])
                ),
                roles: new Set([...solution.roles, role]),
                remaining: solution.remaining.difference(new Set(r2p[role]))
              };
              let new_solution_role_id = [...new_solution.roles].sort().join();
              if (
                new_solution.remaining.size == 0 &&
                !unique_result_role_sets.has(new_solution_role_id)
              ) {
                result.push(new_solution);
              } else {
                new_solution_space.add(new_solution);
              }
              unique_result_role_sets.add(new_solution_role_id);

              steps += 1;
            }
          }
        }
      }
      solution_space = new_solution_space;
    }
    console.log(
      `Finished in ${steps} steps. |R| = ${candidate_roles.length}. |result| = ${result.length}`
    );
    result.forEach(x => {
      x.num_permissions_granted = x.permissions_granted.size;
      x.id = [...x.roles].sort().join(", ");
    });
    return result
      .sort((a, b) => a.permissions_granted.size - b.permissions_granted.size)
      .slice(0, 20);
  };
  $: suggested_roles = role_suggestion_heuristic(selected_permissions, r2p);
</script>

<style>

</style>

<div id="wrapper">
  <Grid fullWidth="false">
    <Row>
      <Column>
        <h3>Search permissions</h3>
        <Form>
          <MultiSelect
            filterable
            titleText="Namespace"
            label="Select GC namespace"
            items={unique_namespaces}
            bind:selectedIds={filtered_namespaces} />
          {#each filtered_namespaces as namespace}
            <Tag type="teal">{unique_namespaces[namespace].text}</Tag>
          {/each}
          <MultiSelect
            filterable
            titleText="Area"
            label="Select GC product area"
            items={unique_areas}
            bind:selectedIds={filtered_areas_ids} />

          {#each filtered_areas as area}
            <Tag type="magenta">{area}</Tag>
          {/each}

          {#if filtered_permissions.length > 0}
            <DataTable
              headers={permission_selector_header}
              rows={permission_selector_rows}>
              <span slot="cell" let:row let:cell>
                {#if cell.key === 'action'}
                  <Button
                    hasIconOnly
                    icon={Add16}
                    size="small"
                    on:click={add_permission(cell.value)} />
                {:else}{cell.value}{/if}
              </span>
            </DataTable>
          {:else}
            <h4>Select namespace and area...</h4>
          {/if}
        </Form>
      </Column>
      <Column>
        <h3>Selected permissions</h3>
        <Button
          icon={TrashCan16}
          kind="danger"
          size="small"
          on:click={() => {
            selected_permissions = [];
          }}>
          Clear selection
        </Button>

        <DataTable
          expandable
          headers={permission_selector_header}
          rows={permission_subset_rows}>
          <div slot="expanded-row" let:row>
            <pre>{JSON.stringify(row, null, 2)}</pre>
          </div>
          <span slot="cell" let:row let:cell>
            {#if cell.key === 'action'}
              <Button
                hasIconOnly
                icon={TrashCan16}
                size="small"
                kind="danger"
                on:click={remove_permission(cell.value)} />
            {:else}{cell.value}{/if}
          </span>
        </DataTable>

      </Column>
      <Column>
        <h3>Suggested roles</h3>
        <DataTable
          expandable
          headers={[
              { key: 'id', value: 'Roles' },
              { key: 'num_permissions_granted', value: '# Permissions Granted' }
          ]}
          rows={suggested_roles}>
          <div slot="expanded-row" let:row>
            Granted permissions:
            <pre>
              {#each [...row.permissions_granted] as permission}
                <li>{permission}</li>
              {/each}
            </pre>
          </div>
        </DataTable>
      </Column>
    </Row>
  </Grid>
</div>
