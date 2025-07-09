import { DOMUtils } from './common';
import type { BranchMapping } from './types';
import { SCHOOL_BRANCHES, ASSESSMENT_BRANCHES, TRAINING_BRANCHES } from './types';

class PackingListFormManager {
  private branchField: HTMLSelectElement | null = null;
  private schoolTypeField: HTMLSelectElement | null = null;
  private assessmentTypeField: HTMLSelectElement | null = null;
  private trainingTypeField: HTMLSelectElement | null = null;
  
  private allSchoolOptions: Array<{value: string, text: string, orig: HTMLOptionElement}> = [];
  private allAssessmentOptions: Array<{value: string, text: string, orig: HTMLOptionElement}> = [];
  private allTrainingOptions: Array<{value: string, text: string, orig: HTMLOptionElement}> = [];

  constructor() {
    this.initialize();
  }

  private initialize(): void {
    this.setupElements();
    this.cacheOptions();
    this.setupEventListeners();
    this.updateTypeOptions();
    this.handleEventTypeChange();
  }

  private setupElements(): void {
    this.branchField = DOMUtils.getElement<HTMLSelectElement>('[name="branch"]');
    this.schoolTypeField = DOMUtils.getElement<HTMLSelectElement>('[name="school_type"]');
    this.assessmentTypeField = DOMUtils.getElement<HTMLSelectElement>('[name="assessment_type"]');
    this.trainingTypeField = DOMUtils.getElement<HTMLSelectElement>('[name="training_type"]');
  }

  private cacheOptions(): void {
    if (this.schoolTypeField) {
      this.allSchoolOptions = this.getOptions(this.schoolTypeField);
    }
    if (this.assessmentTypeField) {
      this.allAssessmentOptions = this.getOptions(this.assessmentTypeField);
    }
    if (this.trainingTypeField) {
      this.allTrainingOptions = this.getOptions(this.trainingTypeField);
    }
  }

  private getOptions(select: HTMLSelectElement): Array<{value: string, text: string, orig: HTMLOptionElement}> {
    return Array.from(select.options).map(opt => ({
      value: opt.value,
      text: opt.text,
      orig: opt
    }));
  }

  private setOptions(
    select: HTMLSelectElement, 
    options: Array<{value: string, text: string, orig: HTMLOptionElement}>, 
    selectedValue: string
  ): void {
    select.innerHTML = '';
    options.forEach(opt => {
      const o = document.createElement('option');
      o.value = opt.value;
      o.text = opt.text;
      if (opt.value === selectedValue) {
        o.selected = true;
      }
      select.appendChild(o);
    });
  }

  private setupEventListeners(): void {
    if (this.branchField) {
      this.branchField.addEventListener('change', this.updateTypeOptions.bind(this));
    }
    // Add event listener for event_type changes
    const eventTypeField = DOMUtils.getElement<HTMLSelectElement>('[name="event_type"]');
    if (eventTypeField) {
      eventTypeField.addEventListener('change', this.handleEventTypeChange.bind(this));
    }
    // Add event listener for assessment_type changes
    if (this.assessmentTypeField) {
      this.assessmentTypeField.addEventListener('change', this.handleAssessmentTypeChange.bind(this));
    }
  }

  private filterOptions(
    select: HTMLSelectElement,
    allOptions: Array<{value: string, text: string, orig: HTMLOptionElement}>,
    branch: string,
    mapping: BranchMapping
  ): void {
    const filtered = allOptions.filter(opt => {
      if (!opt.value) return true; // Keep blank option
      const allowed = mapping[opt.value];
      return allowed && (allowed.includes(branch) || branch === 'all');
    });
    this.setOptions(select, filtered, select.value);
  }

  private updateTypeOptions(): void {
    if (!this.branchField) return;

    const branch = this.branchField.value;

    if (this.schoolTypeField) {
      this.filterOptions(this.schoolTypeField, this.allSchoolOptions, branch, SCHOOL_BRANCHES);
    }
    if (this.assessmentTypeField) {
      this.filterOptions(this.assessmentTypeField, this.allAssessmentOptions, branch, ASSESSMENT_BRANCHES);
    }
    if (this.trainingTypeField) {
      this.filterOptions(this.trainingTypeField, this.allTrainingOptions, branch, TRAINING_BRANCHES);
    }

    this.updateFieldVisibility(branch);
  }

  private updateFieldVisibility(branch: string): void {
    const schoolTypeRow = DOMUtils.getElement<HTMLElement>('#school-type-row');
    const assessmentTypeRow = DOMUtils.getElement<HTMLElement>('#assessment-type-row');
    const trainingTypeRow = DOMUtils.getElement<HTMLElement>('#training-type-row');
    const schoolRow = DOMUtils.getElement<HTMLElement>('#school-row');
    // Robustly find the <p> containing the school_name input
    let schoolNameRow: HTMLElement | null = null;
    const pTags = document.querySelectorAll('form p');
    pTags.forEach(p => {
      if (p.querySelector('[name="school_name"]')) {
        schoolNameRow = p as HTMLElement;
      }
    });

    // Show/hide type-specific rows based on event type
    const eventTypeField = DOMUtils.getElement<HTMLSelectElement>('[name="event_type"]');
    if (eventTypeField) {
      const eventType = eventTypeField.value;
      if (schoolTypeRow) {
        schoolTypeRow.style.display = eventType === 'school' ? 'block' : 'none';
      }
      if (assessmentTypeRow) {
        assessmentTypeRow.style.display = eventType === 'assessment' ? 'block' : 'none';
      }
      if (trainingTypeRow) {
        trainingTypeRow.style.display = eventType === 'training' ? 'block' : 'none';
      }
      // School dropdown only for event_type 'school' and a school_type is selected
      if (schoolRow && this.schoolTypeField) {
        const hasSchoolType = this.schoolTypeField.value && this.schoolTypeField.value !== '';
        schoolRow.style.display = (eventType === 'school' && hasSchoolType) ? 'block' : 'none';
      } else if (schoolRow) {
        schoolRow.style.display = 'none';
      }
      // School name input only for event_type 'school'
      if (schoolNameRow !== null) {
        (schoolNameRow as HTMLElement).style.display = eventType === 'school' ? 'block' : 'none';
      }
    }
  }

  private handleEventTypeChange(): void {
    this.updateTypeOptions();
    // Show/hide custom event type input
    const eventTypeField = DOMUtils.getElement<HTMLSelectElement>('[name="event_type"]');
    const customEventTypeRow = document.querySelector('p:has([name="custom_event_type"])') as HTMLElement;
    if (eventTypeField && customEventTypeRow) {
      customEventTypeRow.style.display = eventTypeField.value === 'other' ? 'block' : 'none';
      // Show/hide assessment type row if assessment selected
      const assessmentTypeRow = DOMUtils.getElement<HTMLElement>('#assessment-type-row');
      if (assessmentTypeRow) {
        assessmentTypeRow.style.display = eventTypeField.value === 'assessment' ? 'block' : 'none';
      }
    }
  }

  private handleAssessmentTypeChange(): void {
    // Show/hide custom event type input if 'other' is selected in assessment_type
    const customEventTypeRow = document.querySelector('p:has([name="custom_event_type"])') as HTMLElement;
    if (this.assessmentTypeField && customEventTypeRow) {
      customEventTypeRow.style.display = this.assessmentTypeField.value === 'other' ? 'block' : 'none';
    }
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new PackingListFormManager();
}); 