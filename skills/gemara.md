# **Skill: Gemara Schema Generator & Auditor**

This skill enables the automated conversion of unstructured security documentation, certification standards, or product manuals into valid **Gemara YAML schemas** (Governance, Compliance, Security, Technical).

## **1 Classification Phase**

When a user provides a file or text, the model must first analyze the content to determine the correct Gemara Layer:

- **Governance**: Strategic policies, high-level standards, risk management frameworks.  
- **Compliance**: Regulatory requirements (SOC2, ISO 27001, HIPAA), industry-specific certifications.  
- **Security**: Technical control objectives, defense-in-depth strategies, architectural security.  
- **Technical**: Implementation-specific configurations, CLI commands, infrastructure-as-code snippets.

## **2 Extraction & Generation Phase**

The model generates the YAML based on the [Gemara project schemas](https://github.com/gemaraproj/gemara).

- **Control Mapping**: Every requirement must be mapped to a `control_id`.  
- **Metadata**: Populate `version`, `author`, `layer`, and `tags`.  
- **Structure**: Adhere strictly to the Gemara indentation and key-value naming conventions.

## **3 Quality Control (QC) Pass**

After generating the YAML, the model must perform a self-audit:

1. **Completeness**: Cross-reference the source document against the YAML to ensure no controls were omitted.
2. **Accuracy**: Verify that the intent of the original requirement is preserved in the YAML `description`.
3. **Validation**: Ensure the YAML is syntax-valid and follows the schema constraints for the identified layer.

## **4 Implementation Prompt (For .cursorrules or System Instruction)**

Use the following block to "prime" your AI assistant:

```
As a Gemara Schema Expert, your goal is to convert source docs into YAML. 
Workflow:
1. ANALYZE: Review the provided text/PDF content. Identify the Gemara layer.
2. DRAFT: Create a YAML file following the Gemara schema for that layer.
3. AUDIT: Create a 'QC Report' where you list:
   - Total controls found in source.
   - Total controls mapped in YAML.
   - Any missing fields or logical gaps found during the pass.
4. FINAL: Output the corrected, finalized YAML file.

Schema Reference: [https://github.com/gemaraproj/gemara](https://github.com/gemaraproj/gemara)
```

## **5 Usage Example**

**User:** "Here is the SOC2 Trust Services Criteria for Security. Convert this to Gemara." **AI:** 1 *Classifies as 'Compliance' layer.* 2 *Maps CC1.1, CC1.2, etc., to Gemara controls.* 3 *Performs QC to ensure metadata like 'evidencerequirements' are included.* 4 *Outputs `soc2-security.yaml`.*