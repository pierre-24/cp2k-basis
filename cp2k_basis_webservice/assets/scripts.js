"use strict";

function apiCall(url) {
    return fetch(`/api${url}`).then(resp => {
        if(!resp.ok) {
            window.alert(`error ${resp.status} while requesting ${resp.url}`);
        } else {
            return resp.json();
        }
    });
}

// template tag, found in https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals
function template(strings, ...keys) {
  return (...values) => {
    const dict = values[values.length - 1] || {};
    const result = [strings[0]];
    keys.forEach((key, i) => {
      const value = Number.isInteger(key) ? values[key] : dict[key];
      result.push(value, strings[i + 1]);
    });
    return result.join("");
  };
}

export class Controller  {
    constructor(data) {
        this.data = data;

        this.futureSelectedElements = [];

        this.elementsSelected = [];
        this.basisSetSelected = null;
        this.basisSetVariants = {};
        this.pseudoSelected = null;
        this.pseudoVariants = {};

        this.infoTpl = template`
            <ul>
                <li><strong>Name:</strong> ${0}</li>
                <li><strong>Description:</strong> ${1}</li>
                <li><strong>References:</strong><ul>${2}</ul></li>
                <li><strong>Source:</strong> <a href="${3}">${3}</a></li>
            </ul>`;

        // interface elements
        this.$basisSetSelect = document.querySelector('#basisSetSelect');
        this.$basisSetSelect.addEventListener('change', () => {
            this.update();
        });

        this.$basisSetSearch = document.querySelector('#basisSetSearch');
        this.$basisSetSearch.addEventListener('keyup', () => {
            this.update();
        });

        this.$pseudoSelect = document.querySelector('#pseudoSelect');
        this.$pseudoSelect.addEventListener('change', () => {
            this.update();
        });

        this.$pseudoSearch = document.querySelector('#pseudoSearch');
        this.$pseudoSearch.addEventListener('keyup', () => {
            this.update();
        });

        this.$basisSetResult = document.querySelector('#basisSetResult');
        this.$basisSetMetadata = document.querySelector('#basisSetMetadata');

        this.$pseudoResult = document.querySelector('#pseudoResult');
        this.$pseudoMetadata = document.querySelector('#pseudoMetadata');

        this.$inputResult = document.querySelector('#inputResult');

        // buttons
        document.querySelectorAll('.copy-button').forEach($e => {
            let $node = document.createElement('i');
            $node.classList.add('bi', 'bi-clipboard');
            $e.append($node);

           $e.addEventListener('click', () => {
               let $src = document.querySelector($e.dataset.textarea);
               navigator.clipboard.writeText($src.value);

               let $icon = $e.querySelector('i.bi-clipboard');
               $icon.classList.remove('bi-clipboard');
               $icon.classList.add('bi-check');

               setTimeout(() => {
                   $icon.classList.remove('bi-check');
                   $icon.classList.add('bi-clipboard');
               }, 3000);
           });
        });

        document.querySelectorAll('.info-button').forEach($e => {
            let $node = document.createElement('i');
            $node.classList.add('bi', 'bi-info-square');
            $e.append($node);
        });


        // cell elements
        document.querySelectorAll('.cell-element').forEach($e => {
            $e.addEventListener('click', () => {
                $e.classList.toggle('selected');
                this.toggleElement($e.dataset.symbol);
            });
        });

        this.$clear = document.querySelector('#clearButton');
        this.$clear.addEventListener('click', () => {
            document.querySelectorAll('.cell-element').forEach($e => {
                $e.classList.remove('selected');
            });

            this.futureSelectedElements = [];

            this.$basisSetSelect.value = null;
            this.$pseudoSelect.value = null;

            this.update();
        });

        // ok, now update
        this.update();
    }

    update() {
        let requiresOutputsUpdate = false;

        // update elements selected
        if (this.futureSelectedElements.toString() !== this.elementsSelected.toString()) {
            requiresOutputsUpdate = true;
            this.elementsSelected = this.futureSelectedElements.slice();
        }

        // update the list of basis sets & pseudo based on the elements that are selected and the search value
        let basisSetSearched = this.$basisSetSearch.value;
        let basisSetValue = this.$basisSetSelect.value;
        this._updateSelect(this.$basisSetSelect, this.data.basis_sets, basisSetValue, basisSetSearched);

        let pseudoSearched = this.$pseudoSearch.value;
        let pseudoValue = this.$pseudoSelect.value;
        this._updateSelect(this.$pseudoSelect, this.data.pseudopotentials, pseudoValue, pseudoSearched);

        // update basis set & pseudo
        if(this.basisSetSelected !== this.$basisSetSelect.value) {
            this.basisSetSelected = this.$basisSetSelect.value;

            let elements = [];
            if (this.basisSetSelected.length > 0)
                elements = this.data.basis_sets.per_name[this.basisSetSelected];

            this._updateAvailability('basis-set', elements);
            requiresOutputsUpdate = true;
        }

        if(this.pseudoSelected !== this.$pseudoSelect.value) {
            this.pseudoSelected = this.$pseudoSelect.value;

            let elements = [];
            if(this.pseudoSelected.length > 0)
                elements = this.data.pseudopotentials.per_name[this.pseudoSelected];

            this._updateAvailability('pseudo', elements);
            requiresOutputsUpdate = true;
        }

        if(requiresOutputsUpdate)
            this._updateOutputs();
    }

    _updateSelect($select, data, prevValue, searchValue) {
        let perName = data.per_name;

        $select.innerHTML = '';
        Object.keys(perName).forEach((name) => {
            if((searchValue.length !== 0 && name.toLowerCase().includes(searchValue.toLowerCase())) || searchValue.length === 0) {
                if(!this.elementsSelected.some(e => perName[name].indexOf(e) < 0)) {
                    let $node = document.createElement('option');
                    $node.value = name;
                    $node.innerText = name;

                    if(name === prevValue)
                        $node.selected = true;

                    $select.append($node);
                }
            }
        });
    }

    _updateAvailability(type, elements) {
        document.querySelectorAll('.cell-element').forEach($e => {
            if(elements.indexOf($e.dataset.symbol) < 0)
                $e.classList.remove(`${type}-avail`);
            else
                $e.classList.add(`${type}-avail`);
        });
    }

    _updateOutputBasisSet(data, metadata) {
        this.$basisSetResult.value = data;
        if(metadata.length > 0)
            this.$basisSetMetadata.innerHTML = this.infoTpl(...metadata);
        else
            this.$basisSetMetadata.innerText = 'Select a basis set to get info.';
    }

    _updateOutputPseudo(data, metadata) {
        this.$pseudoResult.value = data;
        if(metadata.length > 0)
            this.$pseudoMetadata.innerHTML = this.infoTpl(...metadata);
        else
            this.$pseudoMetadata.innerText = 'Select a pseudopotential to get info.';
    }

    _updateOutputInput() {
        let kinds = '';
        this.elementsSelected.forEach(e => {

            let variants = {};
            if(this.basisSetSelected.length > 0 && this.pseudoSelected.length === 0)
                variants = Object.keys(this.basisSetVariants[e]);
            else if(this.basisSetSelected.length === 0 && this.pseudoSelected.length > 0)
                variants = Object.keys(this.pseudoVariants[e]);
            else if(this.basisSetSelected.length > 0 && this.pseudoSelected.length > 0)
                variants = Object.keys(this.basisSetVariants[e]).filter(v => v in this.pseudoVariants[e]);

            let kind = `&KIND ${e}\n`;
            if(variants.length === 0) {
                kind += `# No compatible variant for ${e}: [basis set=${Object.keys(this.basisSetVariants[e])}] and [pseudo=${Object.keys(this.pseudoVariants[e])}].\n`;
            } else {
                /* by default, select the variant with the largest q (least core electrons), since it is the mostly available
                * */
                let variant = `q` + Math.max(...variants.map(e => parseInt(e.substring(1))));

                if(this.basisSetSelected.length > 0) {
                    kind += `  BASIS_SET ${this.basisSetVariants[e][variant]}`;
                    if(variants.length > 1)
                        kind += ` ! or ${variants.filter(v => v !== variant).map(v => this.basisSetVariants[e][v])}`;
                    kind += '\n';
                }

                if(this.pseudoSelected.length > 0) {
                    kind += `  POTENTIAL ${this.pseudoVariants[e][variant]}`;
                    if(variants.length > 1)
                        kind += ` ! or ${variants.filter(v => v !== variant).map(v => this.pseudoVariants[e][v])}`;
                    kind += '\n';
                }
            }

            kind += '&END KIND';

            if(kinds.length > 0)
                kinds += '\n';

            kinds += kind;
        });

        this.$inputResult.value = kinds;
    }

    _fetchMetadata(query, mt) {
        return [
            query.name,
            mt.description,
            mt.references.map(e => `<li><a href="${e}">${e}</a></li>`).join('\n'),
            mt.source
        ];
    }

    _updateOutputs() {
        this.$inputResult.value = 'Select element(s).';

        if(this.basisSetSelected.length === 0)
            this._updateOutputBasisSet('Select a basis set.', []);
        else if(this.elementsSelected.length === 0) {
            apiCall(`/basis/${this.basisSetSelected}/metadata`).then(data => {
                this._updateOutputBasisSet(
                    'Select element(s)',
                    this._fetchMetadata(data.query, data.result)
                );
            });
        }

        if(this.pseudoSelected.length === 0)
            this._updateOutputPseudo('Select a pseudopotential.', []);
        else if(this.elementsSelected.length === 0) {
            apiCall(`/pseudopotentials/${this.pseudoSelected}/metadata`).then(data => {
                this._updateOutputPseudo(
                    'Select element(s)',
                    this._fetchMetadata(data.query, data.result)
                );
            });
        }

        if(this.elementsSelected.length > 0)  {
            if (this.basisSetSelected.length > 0 && this.pseudoSelected.length === 0) {
                apiCall(`/basis/${this.basisSetSelected}/data?elements=${this.elementsSelected}`).then(data => {
                    this._updateOutputBasisSet(
                        data.result.data,
                        this._fetchMetadata(data.query, data.result.metadata)
                    );
                    this.basisSetVariants = data.result.variants;
                    this._updateOutputInput();
                });
            } else if(this.pseudoSelected.length > 0 && this.basisSetSelected.length === 0)  {
                apiCall(`/pseudopotentials/${this.pseudoSelected}/data?elements=${this.elementsSelected}`).then(data => {
                    this._updateOutputPseudo(
                        data.result.data,
                        this._fetchMetadata(data.query, data.result.metadata)
                    );
                    this.pseudoVariants = data.result.variants;
                    this._updateOutputInput();
                });
            } else if (this.basisSetSelected.length > 0 && this.pseudoSelected.length > 0) {
                Promise.all([ // wait for the end of both requests
                    apiCall(`/basis/${this.basisSetSelected}/data?elements=${this.elementsSelected}`),
                    apiCall(`/pseudopotentials/${this.pseudoSelected}/data?elements=${this.elementsSelected}`)
                ]).then(([data_basis, data_pseudo]) => {
                    this._updateOutputBasisSet(
                        data_basis.result.data,
                        this._fetchMetadata(data_basis.query, data_basis.result.metadata)
                    );

                    this._updateOutputPseudo(
                        data_pseudo.result.data,
                        this._fetchMetadata(data_pseudo.query, data_pseudo.result.metadata)
                    );
                    this.basisSetVariants = data_basis.result.variants;
                    this.pseudoVariants = data_pseudo.result.variants;
                    this._updateOutputInput();
                });
            }
        }
    }

    toggleElement(Z) {
        // add or remove in `this.futureSelectedElements`
        let pos = this.futureSelectedElements.indexOf(Z);
        if(pos < 0) {
            this.futureSelectedElements.push(Z);
        } else {
            this.futureSelectedElements.splice(pos, 1);
        }

        this.update();
    }
}
