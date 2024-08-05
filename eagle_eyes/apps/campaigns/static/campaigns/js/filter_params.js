function setIndexes(){
	// Automatically sets indexes to stages present in the page
	indexes = document.getElementsByClassName("form-row field-index")
	for (let i=0; i<indexes.length; i++) {
		input_field = indexes.item(i).querySelector("input")
		input_field.value = i
		input_field.readOnly = true
	}
}

document.addEventListener("formset:added", () => {

	// Set indexes
	setIndexes()

	tables = document.getElementsByClassName("djn-items inline-related djn-table ui-sortable")
	last_table = tables.item(tables.length-1)
	last_table.style.marginBottom = "20px"

	last_table.addEventListener("formset:added", (e) => {
		e.stopPropagation()
		last_tbody = e.target.children.item(e.target.children.length - 3)
		tr = e.target.children.item(0)
		action_td = tr.children.item(1)
		params_td = tr.children.item(2)
		params = params_td.children.item(0)
		params_td.innerHTML = `<select id=${params.id} name=${params.name} required=""></select>`
		action_select = action_td.children.item(0).children.item(0)

		action_select.addEventListener("change", function(e) {

			tr = e.target.parentNode.parentNode.parentNode
			params_td = tr.children.item(2)
			params_select = params_td.children.item(0)
			fetch("/api/v1/campaigns/actions/" + e.target.value)
			.then(response => response.json())
			.then(res => {
				params_select.innerHTML = `<option value="" selected="">---------</option>`
				res.params_list.forEach(item => {
					params_select.innerHTML += `<option value=${item.key}>${item.key}</option>`
				});
			});
		});
	});
});


document.addEventListener("formset:removed", () => {
	// Set indexes
	setIndexes()
});
