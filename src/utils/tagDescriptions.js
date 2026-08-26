export const tagDescriptions = {
  "RAMIS": "Robot-assisted minimally invasive surgery systems.",
  "Commercial": "Available as a marketed, regulatory-cleared product.",
  "Teleoperated": "Surgeon controls instruments remotely via master console.",
  "Multiple ports": "Uses several trocar access points into the patient.",
  "3+ instruments": "Supports at least three concurrently mountable instruments.",
  "Stereo endoscope": "Provides stereoscopic intraoperative imaging.",
  "Mechanical Cartesian manipulation": "Arm kinematics primarily based on Cartesian/linkage design.",
  "Stereo viewer": "Dedicated binocular display for depth perception.",
  "Single patient cart": "All arms mounted on one mobile patient-side base.",
  "Haptic": "Provides tactile or force cues to the operator, doesn't assume full force feedback.",
  "Wristed instruments": "End effector instruments include distal articulation (wrist).",
  "Snake-like instruments": "End effector instruments include snake-like articulation.",
  "Open surgery": "Intended for non-endoscopic (open) surgical approaches.",
  "Mechanical RCM": "Hardware geometry enforces a remote center of motion pivot.",
  "Retired": "No longer produced or clinically supported.",
  "Orthopedic": "Focused on bone and joint related procedures.",
  "Multiple patient carts": "System separates arms across multiple bases.",
  "Stereo display": "Stereoscopic display (flat screen).",
  "Haptic device": "Provides an haptic interface.",
  "Motorized table": "Includes integrated powered patient positioning table.",
  "Single port": "Access via one incision using multi-channel port.",
  "2 instruments": "Supports a maximum of two concurrent instruments.",
  "Collaborative control": "Shares task execution between human and automation.",
  "Force feedback": "Returns quantitative force/torque data to operator.",
  "Mono endoscope": "Monocular endoscopic imaging only.",
  "Mechanical manipulation": "User input is captured mechanically, with or without actuation.",
  "Open console": "Operator interface without enclosed immersive hood.",
  "Research system": "Primarily for laboratory or academic research use.",
  "Software RCM": "Remote center of motion enforced algorithmically, not by hardware.",
  "Semi-autonomous": "Performs subtasks automatically with human supervision.",
  "Open source": "Provides source code openly for modification.",
  "Open architecture": "Designed for extensibility via documented interfaces.",
  "Free hand manipulation": "User input is captured wirelessly or without mechanical linkage.  Doesn't support haptic feedback.",
  "Autonomous": "Capable of executing tasks without direct real-time human input.",
  "Simulation": "Used chiefly for training or procedural rehearsal.",
  "Flexible robot": "Employs flexible continuum or snake-like mechanisms.",
  "Open microsurgery": "Designed for delicate open microsurgical procedures.",
  "Biopsy": "Supports tissue sampling guidance or extraction.",
  "TRUS": "Transrectal ultrasound guidance or manipulation.",
  "Dental": "Focused on dental or oral implant procedures.",
  "Autonomous motion": "Capable of moving independently without human control.",
  "OEM component": "A robotic arm or subsystem sold to medical device manufacturers for integration into their products; not a standalone clinical system.",
  "Ultrasound": "Utilizes or guides ultrasound imaging for diagnostic or therapeutic procedures.",
  "X-Ray": "Utilizes or guides X-ray or fluoroscopic imaging for diagnostic or interventional procedures.",
  "Radiation": "Delivers or utilizes targeted ionizing radiation for radiation therapy or stereotactic radiosurgery."
};

export const usageDescriptions = {
  "Abdominal": "Procedures within the abdominal cavity (e.g., general, colorectal).",
  "Urological": "Procedures involving urinary tract or male reproductive organs.",
  "Gynecological": "Procedures involving female reproductive system.",
  "Transoral": "Access through the mouth for head and neck or airway surgery.",
  "Knee": "Orthopedic interventions focused on the knee joint.",
  "Hip": "Orthopedic procedures involving the hip joint (e.g., replacement).",
  "Shoulder": "Orthopedic procedures involving the shoulder joint.",
  "Lung": "Pulmonary surgical or interventional procedures.",
  "Bronchoscopy": "Endoscopic examination or intervention in bronchial airways.",
  "Thoracic": "Procedures within the chest excluding the heart.",
  "Spine": "Spinal column or vertebral interventions.",
  "Eye": "Ophthalmic microsurgery or ocular interventions.",
  "Prostate": "Procedures targeting the prostate gland.",
  "Dental implant": "Placement or guidance for dental implants.",
  "Neurological": "Brain, spinal cord, or peripheral nervous system surgical procedures (e.g., DBS, SEEG, biopsy).",
  "Microsurgery": "Delicate open microsurgical procedures on small anatomical structures (vessels, nerves, lymphatics)."
};

export function getTagDescription(tagName) {
  return tagDescriptions[tagName] || '';
}

export function getUsageDescription(usageName) {
  return usageDescriptions[usageName] || '';
}
