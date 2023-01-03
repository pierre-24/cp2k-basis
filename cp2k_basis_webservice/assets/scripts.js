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

async function dummy() {
    return null;
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
        this.orbBasisSetSelected = null;
        this.auxBasisSetSelected = null;
        this.pseudoSelected = null;

        this.infoTpl = template`
            <ul>
                <li><strong>Name:</strong> ${0}</li>
                <li><strong>Description:</strong> ${1}</li>
                <li><strong>References:</strong><ul>${2}</ul></li>
            </ul>`;

        // tags
        this.orbBasisSetTags = [];
        Object.values(this.data.orb_basis_sets.tags).forEach($e => {
            $e.forEach($x => {
                if(this.orbBasisSetTags.indexOf($x) < 0)
                    this.orbBasisSetTags.push($x);
            });
        });

        this.pseudoTags = [];
        Object.values(this.data.pseudopotentials.tags).forEach($e => {
            $e.forEach($x => {
                if(this.pseudoTags.indexOf($x) < 0)
                    this.pseudoTags.push($x);
            });
        });

        // interface elements
        this.$orbBasisSetSelect = document.querySelector('#orbBasisSetSelect');
        this.$orbBasisSetSelect.addEventListener('change', () => {
            this.update();
        });

        this.$auxBasisSetSelect = document.querySelector('#auxBasisSetSelect');
        this.$auxBasisSetSelect.addEventListener('change', () => {
            this.update();
        });

        this.$orbBasisSetSearch = document.querySelector('#orbBasisSetSearch');
        this.$orbBasisSetSearch.addEventListener('keyup', () => {
            this.update();
        });

        this.$orbBasisSetTagSelect = document.querySelector('#orbBasisSetTagSelect');
        this.orbBasisSetTags.forEach($k => {
            let $opt = document.createElement('option');
            $opt.value = $k;
            $opt.innerText = $k;
            this.$orbBasisSetTagSelect.appendChild($opt);
        });

        this.$orbBasisSetTagSelect.addEventListener('change', () => {
            this.update();
        });

        this.$addAuxBasisSet = document.querySelector('#addAuxBasisSet');
        this.$orbBasisSetContainer = document.querySelector('#orbBasisSetContainer');
        this.$auxBasisSetContainer = document.querySelector('#auxBasisSetContainer');

        this.$addAuxBasisSet.addEventListener('change', () => {
            if(this.$addAuxBasisSet.checked) {
                this.$orbBasisSetContainer.classList.add('col-lg-6');
                this.$auxBasisSetContainer.classList.remove('d-none');
                this.$auxBasisSetContainer.classList.add('col-lg-6');
            } else {
                this.$orbBasisSetContainer.classList.remove('col-lg-6');
                this.$auxBasisSetContainer.classList.add('d-none');
                this.$auxBasisSetContainer.classList.remove('col-lg-6');

                this.auxBasisSetSelected = null;
                this.$auxBasisSetSelect.value = '';

                this.update();
            }
        });

        this.$pseudoSelect = document.querySelector('#pseudoSelect');
        this.$pseudoSelect.addEventListener('change', () => {
            this.update();
        });

        this.$pseudoSearch = document.querySelector('#pseudoSearch');
        this.$pseudoSearch.addEventListener('keyup', () => {
            this.update();
        });

        this.$pseudoTagSelect = document.querySelector('#pseudoTagSelect');
        this.pseudoTags.forEach($k => {
            let $opt = document.createElement('option');
            $opt.value = $k;
            $opt.innerText = $k;
            this.$pseudoTagSelect.appendChild($opt);
        });

        this.$pseudoTagSelect.addEventListener('change', () => {
            this.update();
        });

        this.$basisSetResult = document.querySelector('#basisSetResult');
        this.$basisSetMetadata = document.querySelector('#basisSetMetadata');

        this.$pseudoResult = document.querySelector('#pseudoResult');
        this.$pseudoMetadata = document.querySelector('#pseudoMetadata');

        this.$inputResult = document.querySelector('#inputResult');

        // buttons
        document.querySelectorAll('.clear-button').forEach($e => {
            $e.title = "Clear search value";
            $e.classList.add('d-none');

            let $node = document.createElement('i');
            $node.classList.add('bi', 'bi-x');
            $e.append($node);

            let $src = document.querySelector($e.dataset.clear);

            $src.addEventListener('keyup', () => {
                if($src.value.length > 0) {
                    $e.classList.remove('d-none');
                } else {
                    $e.classList.add('d-none');
                }
            });

            $e.addEventListener('click', () => {
                $src.value = "";
                $e.classList.add('d-none');
                this.update();
            });
        });

        document.querySelectorAll('.copy-button').forEach($e => {
            $e.title = "Copy content";

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
            $e.title = "Get info";

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

            this.$orbBasisSetSelect.value = null;
            this.$auxBasisSetSelect.value = null;
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
        let basisSetSearched = this.$orbBasisSetSearch.value;
        let basisSetTag = this.$orbBasisSetTagSelect.value;
        let orbBasisSetValue = this.$orbBasisSetSelect.value;
        this._updateSelect(this.$orbBasisSetSelect, this.data.orb_basis_sets, orbBasisSetValue, basisSetSearched, basisSetTag);

        let auxBasisSetValue = this.$auxBasisSetSelect.value;
        this._updateSelect(this.$auxBasisSetSelect, this.data.aux_basis_sets, auxBasisSetValue, '', '');

        let pseudoSearched = this.$pseudoSearch.value;
        let pseudoTag = this.$pseudoTagSelect.value;
        let pseudoValue = this.$pseudoSelect.value;
        this._updateSelect(this.$pseudoSelect, this.data.pseudopotentials, pseudoValue, pseudoSearched, pseudoTag);

        // update basis set & pseudo
        if(this.orbBasisSetSelected !== this.$orbBasisSetSelect.value || this.auxBasisSetSelected !== this.$auxBasisSetSelect.value) {
            this.orbBasisSetSelected = this.$orbBasisSetSelect.value;
            this.auxBasisSetSelected = this.$auxBasisSetSelect.value;

            let elements = [];
            if (this.orbBasisSetSelected.length > 0 && this.auxBasisSetSelected.length === 0)
                elements = this.data.orb_basis_sets.elements[this.orbBasisSetSelected];
            else if(this.auxBasisSetSelected.length > 0 && this.orbBasisSetSelected.length === 0)
                elements = this.data.aux_basis_sets.elements[this.auxBasisSetSelected];
            else if(this.orbBasisSetSelected.length > 0 && this.auxBasisSetSelected.length > 0) {
                this.data.orb_basis_sets.elements[this.orbBasisSetSelected].forEach($e => {
                    if(this.data.aux_basis_sets.elements[this.auxBasisSetSelected].indexOf($e) >= 0)
                        elements.push($e);
                });
            }

            this._updateAvailability('basis-set', elements);
            requiresOutputsUpdate = true;
        }

        if(this.pseudoSelected !== this.$pseudoSelect.value) {
            this.pseudoSelected = this.$pseudoSelect.value;

            let elements = [];
            if(this.pseudoSelected.length > 0)
                elements = this.data.pseudopotentials.elements[this.pseudoSelected];

            this._updateAvailability('pseudo', elements);
            requiresOutputsUpdate = true;
        }

        if(requiresOutputsUpdate)
            this._updateOutputs();
    }

    _updateSelect($select, data, prevValue, searchValue, tagValue) {
        let elements = data.elements;
        let tags = data.tags;

        $select.innerHTML = '';
        Object.keys(elements).forEach((name) => {
            if((searchValue.length > 0 && name.toLowerCase().includes(searchValue.toLowerCase())) || searchValue.length === 0) {
                if(tagValue.length === 0 || (tagValue.length > 0 && tags[name].indexOf(tagValue) >= 0)) {
                    if(!this.elementsSelected.some(e => elements[name].indexOf(e) < 0)) {
                        let $node = document.createElement('option');
                        $node.value = name;
                        $node.innerText = name;

                        if(name === prevValue)
                            $node.selected = true;

                        $select.append($node);
                    }
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
            this.$basisSetMetadata.innerHTML = metadata;
        else
            this.$basisSetMetadata.innerText = 'Select a basis set to get info.';
    }

    _updateOutputPseudo(data, metadata) {
        this.$pseudoResult.value = data;
        if(metadata.length > 0)
            this.$pseudoMetadata.innerHTML = metadata;
        else
            this.$pseudoMetadata.innerText = 'Select a pseudopotential to get info.';
    }

    _updateOutputInput(orb_basis_variants, aux_basis_variants, pseudo_variants) {
        let kinds = '';

        if(orb_basis_variants != null || aux_basis_variants != null || pseudo_variants != null)  {
            let available_variants = [orb_basis_variants, aux_basis_variants, pseudo_variants].filter(vx => vx != null);

            this.elementsSelected.forEach(e => {
                let variants_for_elements = available_variants.map(vx => Object.keys(vx[e]));

                let variants = variants_for_elements[0];
                variants_for_elements.slice(1).forEach(vx => variants = variants.filter(v => vx.indexOf(v) >= 0));

                let kind = `&KIND ${e}\n`;
                if(variants.length === 0) {
                    kind += `  ! Incompatible number of valence electron\n`;
                    if(orb_basis_variants != null)
                        kind += `  ! BASIS_SET ORB ${Object.values(orb_basis_variants[e])}\n`;
                    if(aux_basis_variants != null)
                        kind += `  ! BASIS_SET ${this.data.aux_basis_sets.type[this.auxBasisSetSelected]} ${Object.values(aux_basis_variants[e])}\n`;
                    if(pseudo_variants != null)
                        kind += `  ! POTENTIAL ${Object.values(pseudo_variants[e])}\n`;
                } else {
                    /* by default, select the variant with the largest q (least core electrons), since it is the mostly available
                    * */
                    let variant = `q` + Math.max(...variants.map(e => parseInt(e.substring(1))));

                    if(this.orbBasisSetSelected.length > 0) {
                        kind += `  BASIS_SET ORB ${orb_basis_variants[e][variant]}`;
                        if(variants.length > 1)
                            kind += ` ! or ${variants.filter(v => v !== variant).map(v => orb_basis_variants[e][v])}`;
                        kind += '\n';
                    }

                    if(this.auxBasisSetSelected.length > 0) {
                        kind += `  BASIS_SET ${this.data.aux_basis_sets.type[this.auxBasisSetSelected]} ${aux_basis_variants[e][variant]}`;
                        if(variants.length > 1)
                            kind += ` ! or ${variants.filter(v => v !== variant).map(v => aux_basis_variants[e][v])}`;
                        kind += '\n';
                    }

                    if(this.pseudoSelected.length > 0) {
                        kind += `  POTENTIAL ${pseudo_variants[e][variant]}`;
                        if(variants.length > 1)
                            kind += ` ! or ${variants.filter(v => v !== variant).map(v => pseudo_variants[e][v])}`;
                        kind += '\n';
                    }
                }

                kind += '&END KIND';

                if(kinds.length > 0)
                    kinds += '\n';

                kinds += kind;
            });
        }

        this.$inputResult.value = kinds;
    }

    _makeMetadata(query, mt) {
        return this.infoTpl(...[
            query.name,
            mt.description,
            mt.references.map(e => `<li><a href="${e}">${e}</a></li>`).join('\n')
        ]);
    }

    _updateOutputs() {
        this.$inputResult.value = 'Select element(s).';
        let promises = [];

        if(this.elementsSelected.length === 0) {
            // prepare all promises
            if(this.orbBasisSetSelected.length !== 0)
                promises.push(apiCall(`/basis/${this.orbBasisSetSelected}/metadata`));
            else
                promises.push(dummy());

            if(this.auxBasisSetSelected.length !== 0)
                promises.push(apiCall(`/basis/${this.auxBasisSetSelected}/metadata`));
            else
                promises.push(dummy());

            if(this.pseudoSelected.length !== 0)
                promises.push(apiCall(`/pseudopotentials/${this.pseudoSelected}/metadata`));
            else
                promises.push(dummy());

            // fire all!
            Promise.all(promises).then(([orb_basis_mt, aux_basis_mt, pseudo_mt]) => {
                if(orb_basis_mt == null && aux_basis_mt == null)
                    this._updateOutputBasisSet('Select a basis set.', '');
                else {
                    let metadata = '';
                    if(orb_basis_mt != null)
                        metadata += this._makeMetadata(orb_basis_mt.query, orb_basis_mt.result);
                    if(aux_basis_mt != null)
                        metadata += this._makeMetadata(aux_basis_mt.query, aux_basis_mt.result);

                    this._updateOutputBasisSet(
                        'Select element(s)',
                        metadata
                    );
                }

                if(pseudo_mt != null) {
                    this._updateOutputPseudo(
                        'Select element(s)',
                        this._makeMetadata(pseudo_mt.query, pseudo_mt.result)
                    );
                } else {
                    this._updateOutputPseudo('Select a pseudopotential.', '');
                }
            });
        } else {
            // prepare all promises
            if(this.orbBasisSetSelected.length !== 0)
                promises.push(apiCall(`/basis/${this.orbBasisSetSelected}/data?elements=${this.elementsSelected}`));
            else
                promises.push(dummy());

            if(this.auxBasisSetSelected.length !== 0)
                promises.push(apiCall(`/basis/${this.auxBasisSetSelected}/data?elements=${this.elementsSelected}`));
            else
                promises.push(dummy());

            if(this.pseudoSelected.length !== 0)
                promises.push(apiCall(`/pseudopotentials/${this.pseudoSelected}/data?elements=${this.elementsSelected}`));
            else
                promises.push(dummy());

            // fire all!
            Promise.all(promises).then(([orb_basis_data, aux_basis_data, pseudo_data]) => {
                let orb_basis_variants = null;
                let aux_basis_variants = null;
                let pseudo_variants = null;

                if(orb_basis_data == null && aux_basis_data == null)
                    this._updateOutputBasisSet('Select a basis set.', '');
                else {
                    let data = '';
                    let metadata = '';

                    if(orb_basis_data != null) {
                        data += orb_basis_data.result.data;
                        metadata += this._makeMetadata(orb_basis_data.query, orb_basis_data.result.metadata);
                        orb_basis_variants = orb_basis_data.result.variants;
                    }

                    if(aux_basis_data != null) {
                        data += aux_basis_data.result.data;
                        metadata += this._makeMetadata(aux_basis_data.query, aux_basis_data.result.metadata);
                        aux_basis_variants = aux_basis_data.result.variants;
                    }

                    this._updateOutputBasisSet(data, metadata);
                }

                if(pseudo_data != null) {
                    this._updateOutputPseudo(
                        pseudo_data.result.data,
                        this._makeMetadata(pseudo_data.query, pseudo_data.result.metadata)
                    );
                    pseudo_variants = pseudo_data.result.variants;
                } else {
                    this._updateOutputPseudo('Select a pseudopotential.', '');
                }

                this._updateOutputInput(orb_basis_variants, aux_basis_variants, pseudo_variants);
            });
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
