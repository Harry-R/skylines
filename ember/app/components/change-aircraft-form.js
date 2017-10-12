import Ember from 'ember';
import { validator, buildValidations } from 'ember-cp-validations';
import { task } from 'ember-concurrency';

const Validations = buildValidations({
  registration: {
    descriptionKey: 'registration',
    validators: [
      validator('length', { max: 32 }),
    ],
    debounce: 500,
  },
  competitionId: {
    descriptionKey: 'competition-id',
    validators: [
      validator('length', { max: 5 }),
    ],
    debounce: 500,
  },
});

export default Ember.Component.extend(Validations, {
  ajax: Ember.inject.service(),

  classNames: ['panel-body'],

  fixCalc: null,

  flightId: null,
  models: null,
  modelId: null,
  registration: null,
  competitionId: null,
  onDidSave() {},

  error: null,

  actions: {
    async submit() {
      let { validations } = await this.validate();
      if (validations.get('isValid')) {
        this.get('saveTask').perform();
      }
    },
  },

  saveTask: task(function * () {
    let id = this.get('flightId');
    let json = this.getProperties('modelId', 'registration', 'competitionId');

    try {
      yield this.get('ajax').request(`/api/flights/${id}/`, { method: 'POST', json });
      this.get('onDidSave')();

      let fixCalc = this.get('fixCalc');

      fixCalc.removeFlight(id);
      fixCalc.addFlightFromJSON(`/api/flights/${id}/json`);


    } catch (error) {
      this.set('error', error);
    }
  }).drop(),
});
