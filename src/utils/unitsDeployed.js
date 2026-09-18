/**
 * Utility functions for formatting and categorizing units deployed.
 */

/**
 * Returns the category range string for a given deployment count.
 * Categories match the established MedMachina groupings:
 * 0-10, 10-50, 50-100, 100-500, 500-1000, 1000+
 *
 * @param {number|null|undefined} count
 * @returns {string}
 */
export function getUnitsCategory(count) {
  if (count == null || typeof count !== 'number') return '';
  if (count >= 1000) return '1000+';
  if (count >= 500) return '500-1000';
  if (count >= 100) return '100-500';
  if (count >= 50) return '50-100';
  if (count >= 10) return '10-50';
  if (count >= 0) return '0-10';
  return '';
}

/**
 * Returns tooltip text for a units deployed object { count, source_url }.
 *
 * @param {object|null|undefined} unitsDeployed
 * @returns {string}
 */
export function getUnitsDeployedTooltip(unitsDeployed) {
  if (!unitsDeployed || unitsDeployed.count == null) return '';
  const category = getUnitsCategory(unitsDeployed.count);
  return `${category} (~${unitsDeployed.count.toLocaleString()} units deployed)`;
}
