"use strict";

function apiCall(url) {
    return fetch(`/api${url}`).then(resp => {
        if(!resp.ok) {
            alert(`error ${resp.status} while requesting ${resp.url}`);
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
        this.pseudoSelected = null;

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

        // copy buttons
        document.querySelectorAll('.copy-button').forEach($e => {
           $e.addEventListener('click', () => {
               let $src = document.querySelector('#' + $e.dataset.textarea);
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

        // cell elements
        document.querySelectorAll('.cell-element').forEach($e => {
            $e.addEventListener('click', () => {
                $e.classList.toggle('selected');
                this.toggleElement($e.dataset.symbol);
            });
        });

        this.$elementsClear = document.querySelector('#elementsClear');
        this.$elementsClear.addEventListener('click', () => {
            document.querySelectorAll('.cell-element').forEach($e => {
                $e.classList.remove('selected');
            });

            this.futureSelectedElements = [];
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

    _updateOutputs() {
        this.$basisSetResult.innerText = 'Select element(s).';
        this.$pseudoResult.innerText = 'Select element(s).';
        this.$inputResult.innerText = 'Select element(s).';

        const infoTpl = template`<strong>Name:</strong> ${0}<br><strong>Description:</strong> ${1}`;

        if(this.elementsSelected.length === 0) {
            if(this.basisSetSelected.length > 0) {
                apiCall(`/basis/${this.basisSetSelected}/metadata`).then(data => {
                    this.$basisSetMetadata.innerHTML = infoTpl(data.query.name, data.result.description);
                });
            } else {
                this.$basisSetMetadata.innerHTML = '';
            }

            if(this.pseudoSelected.length > 0) {
                apiCall(`/pseudopotentials/${this.pseudoSelected}/metadata`).then(data => {
                    this.$pseudoMetadata.innerHTML = infoTpl(data.query.name, data.result.description);
                });
            } else {
                this.$pseudoMetadata.innerText = '';
            }
        } else {
            if(this.basisSetSelected.length === 0) {
                this.$basisSetResult.innerText = 'Select a basis set';
                this.$basisSetMetadata.innerHTML = '';
            } else {
                apiCall(`/basis/${this.basisSetSelected}/data?elements=${this.elementsSelected}`).then(data => {
                    this.$basisSetResult.innerHTML = data.result.data;
                    this.$basisSetMetadata.innerHTML = infoTpl(data.query.name, data.result.metadata.description);
                });
            }

            if(this.pseudoSelected.length === 0) {
                this.$pseudoResult.innerText = 'Select a pseudopotential';
                this.$basisSetMetadata.innerHTML = '';
            } else {
                apiCall(`/pseudopotentials/${this.pseudoSelected}/data?elements=${this.elementsSelected}`).then(data => {
                    this.$pseudoResult.innerHTML = data.result.data;
                    this.$pseudoMetadata.innerHTML = infoTpl(data.query.name, data.result.metadata.description);
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
