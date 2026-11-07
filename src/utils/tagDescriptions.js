export const categoryDescriptions = {
  "RAMIS": "Soft-tissue laparoscopic and single-port robot-assisted minimally invasive surgery systems.",
  "Orthopedic, Spine & Cranial": "Hard-tissue bone-milling, trajectory-alignment, stereotactic cranial, and dental implant systems.",
  "Flexible & Endoluminal": "Continuum and steerable natural-orifice robotic platforms for GI endoscopy and bronchoscopy.",
  "Percutaneous, Diagnostic & Radiosurgery": "Percutaneous needle/biopsy guidance, autonomous ultrasound/venipuncture, and robotic radiosurgery systems.",
  "Microsurgery & Ophthalmic": "High-motion-scaling open microsurgical and intraocular surgical platforms.",
  "Endovascular & Catheter": "Robotic guidewire and catheter manipulation systems for vascular interventions.",
  "OEM & Haptic Subsystems": "Non-clinical robotic arms and haptic master interfaces integrated as building blocks into medical systems.",
  "Simulation & Training": "Virtual-reality and haptic surgical training simulators."
};

export const tagDescriptions = {
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
  "Multiple patient carts": "System separates arms across multiple bases.",
  "Stereo display": "Stereoscopic display (flat screen).",
  "Haptic device": "Provides a haptic master or tactile interface.",
  "Robotic arm": "Standalone serial or collaborative robotic manipulator arm subsystem.",
  "Table-mounted": "Manipulator mounts directly onto the operating table rather than a floor-standing cart.",
  "Handheld": "Handheld robotic or articulating instrument operated directly in the clinician's hand without a floor cart.",
  "Optical navigation": "Integrates optical camera tracking of fiducial markers for registration and tool guidance.",
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
  "Free hand manipulation": "User input is captured wirelessly or without mechanical linkage. Doesn't support haptic feedback.",
  "Autonomous": "Capable of executing tasks without direct real-time human input.",
  "Biopsy": "Supports tissue sampling guidance or extraction.",
  "TRUS": "Transrectal ultrasound guidance or manipulation.",
  "Autonomous motion": "Capable of moving independently without human control.",
  "Ultrasound": "Utilizes or guides ultrasound imaging for diagnostic or therapeutic procedures.",
  "X-Ray": "Utilizes or guides X-ray or fluoroscopic imaging for diagnostic or interventional procedures.",
  "Radiation": "Delivers or utilizes targeted ionizing radiation for radiation therapy or stereotactic radiosurgery.",
  "Natural orifice": "Accesses the surgical site through a natural body opening (mouth, anus, urethra, vagina) without external incisions (NOTES/POET).",
  "Add-on system": "A robotic module designed to attach to and augment an existing conventional device (e.g., endoscope), rather than function as a standalone system.",
  "Capsule": "Swallowable or micro-scale robotic system designed to be ingested or passed through a natural orifice and navigated from outside."
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
  "Microsurgery": "Delicate open microsurgical procedures on small anatomical structures (vessels, nerves, lymphatics).",
  "Endovascular": "Catheter-based and wire-guided interventional procedures within blood vessels (e.g., coronary, peripheral, aortic).",
  "Neurovascular": "Catheter-based or interventional procedures within cerebral and intracranial vasculature (e.g., stroke thrombectomy, aneurysm embolization).",
  "Cardiovascular": "Surgical or interventional procedures involving the heart, cardiac valves, and coronary arteries.",
  "Upper GI": "Endoscopic or surgical procedures targeting the esophagus, stomach, and duodenum (e.g., EGD, ESG, gastric ESD/EMR).",
  "Colorectal": "Endoscopic or surgical procedures targeting the colon, rectum, and anal canal (e.g., colonoscopy, colonic ESD/EMR, colectomy)."
};

export function getCategoryDescription(categoryName) {
  return categoryDescriptions[categoryName] || '';
}

export function getTagDescription(tagName) {
  return tagDescriptions[tagName] || '';
}

export function getUsageDescription(usageName) {
  return usageDescriptions[usageName] || '';
}
