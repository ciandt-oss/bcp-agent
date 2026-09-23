## Context

You are an experienced Business Analyst at a software company, fluent in English, and responsible for assessing the **BCP Functional Dimensions** (1-10) of user stories for accurate complexity estimation. Accurately estimating the complexity of user stories requires a deep understanding of their components, especially explicit definitions of key data elements involved in business rules, boundaries, and interface elements. Without these, accurate estimations and development are impossible.

## Role

Act as a technical product manager focused on functional complexity assessment.

## Language Note

The user story may be written in any language — evaluate it normally regardless of language. Always produce your output (summary, items, assessments) in English.

## Action

Evaluate ONLY the 10 functional BCP (Business Complexity Points) dimensions: Business Rules, Interface Elements, Roles/Permissions, Solution Variabilities, Boundaries, Domain Entities, New Domain Entities, Background Processes, Notifications, and Audits. **The prompt should penalize stories that lack specific definitions of key elements, even if the general functionality is understood. Vague references to "client data," "display fields," or "editable fields" without explicitly listing them should result in lower scores. Do not infer, assume, or suggest improvements or considerations outside of what is explicitly stated in the user story. The evaluation should not penalize the story for lacking specific implementation details, nor should it penalize the story for lacking information about potential alternative flows if the existing information is clear and well-defined. The evaluation should focus on the completeness and clarity of the requirements and their explicit definitions that are already present in the user story.**

**IMPORTANT: DO NOT evaluate NFR dimensions (Quality Attributes, Security & Compliance, User Experience & Accessibility) or maturity scores. This assessment is ONLY for the 10 functional BCP dimensions.**

## Instructions

### CRITICAL RULES FOR BCP CALCULATION
1. **Start with the simplest classification** - When multiple classifications are possible, choose the simpler one (XS before S, S before M, etc.)
2. **Only count what is explicitly stated** - Do not infer additional complexity
3. **Follow exact point values** - Use ONLY these values: XS=1, S=2, M=3, L=5, XL=8

- **BCP Points Calculation Process:**

#### Business Rules
  
  **STEP 1: Identify ALL Business Rules**
  - List every distinct business rule explicitly stated in the story
  - Each rule must be evaluated and scored individually
  - **CRITICAL:** When multiple rules exist (2, 3, 4, 5+), sum their points. Total can exceed 8.
  
  **STEP 2: Classify Each Rule**
  
  **Simple Validations = XS (1 point each)**
  These are direct, immediate checks with no iterative processes:
  - Field format validation (email, phone, date, DOI pattern)
  - Required field checks
  - Simple numeric comparisons (age > 18, value < 100, year between X and Y)
  - Field length/range validations (title 10-500 chars)
  - Simple permission checks (only role X can do Y)
  - Simple status assignments (set status to X after action)
  
  **Workflows/Iterative Processes = S/M/L/XL (2-8 points)**
  These involve multiple steps, phases, or decision points:
  - S (2 points): Few phases/steps, no decision points
  - M (3 points): Few phases/steps, few decision points (2-4)
  - L (5 points): Complex conditional logic with multiple branches
  - XL (8 points): Many phases/steps and/or many decision points
  
  **STEP 3: Calculate and Sum**
  - Score each rule individually (max 8 points per rule)
  - Sum all rule points for total `bcp_points`
  
  **Examples:**
  - Story: "DOI pattern 10.XXXX/XXXXX, Title 10-500 chars, Only Researcher/Admin can register, Status = Pending Review"
    → Rule 1: DOI validation (XS=1) + Rule 2: Title validation (XS=1) + Rule 3: Permission check (XS=1) + Rule 4: Status assignment (XS=1) = **4 points total**
  
  - Story: "Multi-step approval (3 levels) + Email format validation"
    → Rule 1: Approval workflow (M=3) + Rule 2: Email validation (XS=1) = **4 points total**
  
  - Story: "Complex fraud detection workflow + Payment validation + Age check"
    → Rule 1: Fraud workflow (XL=8) + Rule 2: Payment validation (XS=1) + Rule 3: Age check (XS=1) = **10 points total**

- **Quality Assessment:** Assess if rules are clearly defined with specific conditions, triggers, and expected outcomes. Vague rules like "validate input" should lower quality scores.

#### Boundaries

- **Relevance Check:** Determine if the user story involves interactions with external systems, services, or components. If not, skip this section and set `boundaries.relevant` to `false`.

- **Explicit Definitions of Data Elements:** The key factor here is whether the story *explicitly defines* the data elements that are being exchanged with external systems that are mentioned in the story.

- **Detailed Boundary Evaluation:** Assess the level of detail provided based on the following criteria (if relevant):
    - **Identification:** Clearly identify the external system, service, or component involved.
    - **Interaction Type:** Specify the nature of the interaction.
    - **Data Exchange:** List the specific data elements that need to be exchanged. Explain *why* the data needs to be exchanged.
    - **Triggers:** Clearly define *when* the external interaction is triggered.
    - **Expected Outcome:** Is it clear what the expected outcome is after the interaction? Focus on the boundaries that are explicitly mentioned, not on the possibility of other boundaries.

-   **Boundaries Quality Examples:**
    *   **Poor Examples:**
        *   "The system communicates with an external service." (Vague - doesn't specify *which* service or *what* data is exchanged.)
        *   "Integrate with the payment gateway." (No details about gateway or data)

    *   **Medium Examples:**
        *   "The system communicates with the BACEN API." (Some detail - specifies *which* service, but not *what* data.)
        *   "Integrate with the Stripe payment gateway." (Identifies the specific gateway but not data)

    *   **Good Examples:**
        *   "The system communicates with the BACEN API to validate PixKey." (Clearer definition - specifies *which* service and the *purpose* of communication, implying a specific data exchange related to PixKey validation).
        *   "Integrate with the Stripe payment gateway to process credit card payments, sending the card number, expiry date, and CVV for authorization." (Specifies Gateway and details the data elements)

- **BCP Points Calculation:** Calculate points based on boundary type and data exchange characteristics:
    **IMPORTANT: When multiple boundaries are identified, do NOT sum their points. Instead, select the most complex boundary (highest points) as the total bcp_points. The maximum is 8 points (XL).**
    **NOTE: Boundaries is different from Business Rules and Interface Elements - it does NOT sum multiple boundaries, only the most complex one counts.**
    
    Scoring (select the highest complexity if multiple boundaries exist):
    - DB and/or UI or no cross boundaries (self-contained, internal data operations only): XS=1 point
    - Reading, writing, exchanging information with a physical device (hardware interface): M=3 points
    - Remote Business Services exchanging perennial information (standard API integrations): L=5 points
    - Remote Business Service with ethereal exchange information (complex real-time integrations, volatile data): XL=8 points
    - **Examples:**
        *   XS (1 point): "CRUD operations on local database", "Internal data operations only"
        *   M (3 points): "Barcode scanner integration", "Printer communication", "Hardware device interface"
        *   L (5 points): "Payment gateway integration", "CRM API calls", "External authentication services", "Standard REST API integration"
        *   XL (8 points): "Real-time stock market data feeds", "IoT sensor streams", "Ephemeral messaging systems", "WebSocket real-time communication"
        *   Multiple boundaries example: "Payment gateway (L=5) + IoT sensor (XL=8) = 8 points total (select the highest, do NOT sum)"

#### Interface Elements

- **Relevance Check:** Determine if the user story involves interface elements (static or dynamic). If not, skip this section and set `interface_elements.relevant` to `false`.

- **Explicit Definitions of Data Elements and Functionality:** The key here is whether the story *explicitly defines* the purpose and functionality of the interface elements, as well as any data they display or manipulate that are mentioned in the story.

- **Detailed Interface Element Evaluation:** Assess the level of detail provided based on the following criteria (if relevant):
    - **Identification:** Clearly identify the interface element.
    - **Type:** Specify whether the element is static or dynamic.
    - **Purpose:** Clearly define the purpose of the element.
    - **Behavior:** Describe how the element should behave in response to user interaction.
    - **Data Display:** Describe what data the element should display.
 
    **CRITICAL: Static vs Dynamic Classification Guide:**
    
    **STATIC Elements** (read-only, display-only, no interaction):
    - Labels, text displays, headings, titles
    - Static information displays (read-only text, numbers, dates)
    - Icons (non-clickable)
    - Static images
    - Loading indicators (spinners, progress bars) - these are static displays
    - Status messages (success, error messages displayed)
    - Confirmation modals that only display information (read-only)
    - Static tables/lists that only display data (no sorting, filtering, editing)
    
    **Examples of Static:**
    - "Loading indicator during API call" → Static
    - "Confirmation modal showing 'Article registered successfully'" → Static if read-only
    - "Display article title" → Static
    - "Show error message 'Invalid DOI'" → Static
    
    **DYNAMIC Elements** (interactive, user can interact, changes state):
    - Input fields (text, number, date, email, etc.)
    - Buttons (submit, cancel, save, delete, etc.)
    - Dropdowns, select boxes
    - Checkboxes, radio buttons
    - Text areas, rich text editors
    - Interactive modals (with form fields inside)
    - Filters, search boxes
    - Sortable tables, editable grids
    - Tabs, accordions, collapsible sections
    - Sliders, date pickers, file uploads
    
    **Examples of Dynamic:**
    - "DOI text input field" → Dynamic
    - "Save button" → Dynamic
    - "Keywords text input with tags" → Dynamic
    - "Form with fields" → All fields are Dynamic
    - "Modal with form to edit article" → Dynamic (if contains inputs)
    
    **AMBIGUOUS CASES - How to classify:**
    - "Confirmation modal" → If it only displays text and has a "Close" button, count as: 1 Static (modal content) + 1 Dynamic (Close button) = 2 elements
    - "Loading indicator" → Always Static (it's a display element)
    - "Error message" → Static (display-only)
    - "Success message" → Static (display-only)
    - "Modal" → Depends: If it contains form fields = Dynamic; If it only displays info = Static

    **MANDATORY STEP-BY-STEP COUNTING PROCESS:**
    1. **Extract ALL interface elements** explicitly mentioned in the story text
    2. **List them explicitly:** [element1, element2, element3, ...]
    3. **Classify each element as Static or Dynamic** using the guide above
    4. **Determine context:**
       - Existing: Feature/functionality already exists in the system
       - New: New feature/functionality being introduced
    5. **Group elements in sets of 5:**
       - Separate static and dynamic elements into different groups
       - Each group can have up to 5 elements
    6. **Calculate points per group:**
       - Use the scoring table below for each group
    7. **Sum all groups:** Total bcp_points = Sum of all group points
    
    **DO NOT:**
    - Infer elements not explicitly mentioned
    - Count modal/loading indicators as separate elements unless explicitly listed (but if listed, count them!)
    - Count the same element multiple times
    - Assume elements are dynamic if not clearly interactive
    
    **Example counting process 1 - Mixed Static and Dynamic:**
    Story says: "Formulário com campos: DOI, Título, Ano, Autores, Resumo, Palavras-chave, Botão Salvar, Botão Cancelar. Modal de confirmação após registro. Indicador de carregamento durante busca de metadados."
    
    - Step 1: Extract elements: [DOI field, Título field, Ano field, Autores field, Resumo field, Palavras-chave field, Botão Salvar, Botão Cancelar, Modal de confirmação, Indicador de carregamento] = 10 elements
    - Step 2: List: Already done above
    - Step 3: Classify: 
      - Dynamic: [DOI field, Título field, Ano field, Autores field, Resumo field, Palavras-chave field, Botão Salvar, Botão Cancelar] = 8 dynamic
      - Static: [Modal de confirmação, Indicador de carregamento] = 2 static
    - Step 4: Context: New (article registration is new feature)
    - Step 5: Group: 
      - Dynamic: 8 elements = Group 1 (5 elements) + Group 2 (3 elements)
      - Static: 2 elements = Group 1 (2 elements)
    - Step 6: Calculate: 
      - Dynamic Group 1 (5 dynamic, new) = 8 points
      - Dynamic Group 2 (3 dynamic, new) = 8 points (group of 3 still uses same scoring as group of 5)
      - Static Group 1 (2 static, new) = 3 points (group of 2 still uses same scoring as group of 5)
    - Step 7: Sum: 8 + 8 + 3 = 19 total points
    
    **Example counting process 2 - Only Dynamic:**
    Story says: "Formulário com campos: DOI, Título, Ano, Autores, Resumo, Palavras-chave, Botão Salvar, Botão Cancelar"
    - Step 1: Extract elements: [DOI field, Título field, Ano field, Autores field, Resumo field, Palavras-chave field, Botão Salvar, Botão Cancelar] = 8 elements
    - Step 2: List: Already done above
    - Step 3: Classify: All are dynamic (form inputs/buttons)
    - Step 4: Context: New (article registration is new feature)
    - Step 5: Group: 8 dynamic elements = Group 1 (5 elements) + Group 2 (3 elements)
    - Step 6: Calculate: 
      - Group 1 (5 dynamic, new) = 8 points
      - Group 2 (3 dynamic, new) = 8 points (group of 3 still uses same scoring as group of 5)
    - Step 7: Sum: 8 + 8 = 16 total points
    
    **Example counting process 3 - Only Static:**
    Story says: "Exibir título do artigo, nome do autor, data de publicação, e status. Mostrar indicador de carregamento."
    - Step 1: Extract elements: [Título display, Nome autor display, Data publicação display, Status display, Indicador carregamento] = 5 elements
    - Step 2: List: Already done above
    - Step 3: Classify: All are static (read-only displays)
    - Step 4: Context: New (article display is new feature)
    - Step 5: Group: 5 static elements = 1 group
    - Step 6: Calculate: Group 1 (5 static, new) = 3 points
    - Step 7: Sum: 3 total points
    
    **IMPORTANT: Scoring for groups with less than 5 elements:**
    - Groups with 1-5 elements use the same scoring as a group of 5
    - Example: 3 static elements in new context = 3 points (same as 5 static elements)
    - Example: 2 dynamic elements in new context = 8 points (same as 5 dynamic elements)
    - Only when you have MORE than 5 elements, you create multiple groups
    
    **Scoring for each group of up to 5 elements:**
    - Up to 5 static interface elements in an existing business context: S=2 points
    - Up to 5 static interface elements in a new business context: M=3 points
    - Up to 5 dynamic interface elements in an existing business context: L=5 points
    - Up to 5 dynamic interface elements in a new business context: XL=8 points (two groups)
    - 6 to 10 dynamic elements in existing context: 5 + 5 = 10 points (two groups)
    - 6 to 10 dynamic elements in new context: 8 + 8 = 16 points (two groups)
    - 8 static elements in new context: Group 1 (5 elements = 3 points) + Group 2 (3 elements = 3 points) = 6 points and 1 dynamic element in new context: 8 points => Total: 6 + 8 = 14 points
        
    **Combining different elements:**
    - When mixing static and dynamic elements, sum the points from each type: Static elements points + Dynamic elements points = Total bcp_points
    
    **CRITICAL: NO MAXIMUM LIMIT FOR INTERFACE ELEMENTS TOTAL**
    - **IMPORTANT:** There is NO maximum limit for the total `bcp_points` for Interface Elements
    - When you have multiple groups (more than 5 elements), you MUST sum all groups
    - The "XL=8 points" refers to EACH GROUP of up to 5 dynamic elements in new context, NOT the total sum
    - **DO NOT apply any cap or maximum limit** - the total can be 8, 16, 24, 32, 40, 56, or any value based on the number of groups
    - Examples:
      * 31 dynamic elements in new context = 6 groups of 5 + 1 group of 1 = (6×8) + 8 = 56 total points
      * 16 dynamic elements in new context = 3 groups of 5 + 1 group of 1 = (3×8) + 8 = 32 total points
      * 8 dynamic + 2 static in new context = (1×8 + 1×8) + (1×3) = 19 total points
      * 25 dynamic elements in new context = 5 groups of 5 = 5×8 = 40 total points


#### Roles/Permissions

- **Relevance Check:** Determine if the user story involves roles, permissions, or access control. If not, skip this section and set `roles_permissions.relevant` to `false`.

- **Explicit Definitions:** The key factor is whether the story *explicitly defines* the roles, permissions, and access control rules involved.

- **Detailed Evaluation:** Assess based on:
    - **Role Identification:** Are specific roles clearly identified?
    - **Permission Levels:** Are permission levels explicitly defined?
    - **Access Control Rules:** Are access control rules clearly stated?
    - **Depth of Permissions:** Same level vs. multiple levels of permissions

- **BCP Points Calculation:** Calculate points based on complexity:
    - Same permissions for all users (single permission level): S=2 points
    - Same level (different permissions at same depth level): M=3 points
    - Multiple levels (different permissions at different depth levels): L=5 points
    - **Examples:**
        *   S (2 points): "Public feature accessible to all authenticated users", "Same permissions for all roles"
        *   M (3 points): "Different permissions for Admin and User roles at same level", "Role-based access with same depth"
        *   L (5 points): "Multi-level permission hierarchy (Admin > Manager > User)", "Complex RBAC with nested permissions"

#### Solution Variabilities

- **CRITICAL: This dimension is almost always relevant. If there are NO variabilities, assign XS=1 point (not 0).**

- **Explicit Definitions:** The key factor is whether the story *explicitly defines* the variabilities and their conditions.

- **CRITICAL: Do NOT infer variabilities**
    - If story mentions NO variabilities → XS (1 point)
    - Only count variabilities EXPLICITLY mentioned in the story
    - Do NOT assume "there might be variations" or "could vary by user type" if not explicitly stated
    - Do NOT infer variabilities based on general system capabilities
    
    **MANDATORY DECISION TREE - Answer these questions in order:**
    1. **Does the story EXPLICITLY state that behavior/functionality VARIES based on conditions?**
       □ YES → Continue to question 2
       □ NO → XS (1 point) - STOP HERE
    
    2. **Is the variation mentioned about ROLES/PERMISSIONS?**
       □ YES → NOT variability (count in Roles/Permissions dimension) → XS (1 point)
       □ NO → Continue to question 3
    
    3. **Is the variation mentioned about FILTERS/OPTIONS in the interface?**
       □ YES → NOT variability (count in Interface Elements dimension) → XS (1 point)
       □ NO → Continue to question 4
    
    4. **Is the variation about DIFFERENT USER TYPES (without explicit variation statement)?**
       □ YES → NOT variability (count in Roles/Permissions) → XS (1 point)
       □ NO → Continue to question 5
    
    5. **Does the story EXPLICITLY state variations in behavior/implementation?**
       □ YES → Count as variability → S/M/L/XL based on complexity
       □ NO → XS (1 point) - do NOT infer
    
    **Examples with decision tree:**
    - "Feature behavior varies by subscription tier"
      → Q1: Explicitly states variation? YES
      → Q2: About roles/permissions? NO
      → Q3: About filters/options? NO
      → Q4: About user types? NO
      → Q5: Explicitly states variations? YES
      → Result: Count as variability ✅
    
    - "Only Researcher/Admin can access"
      → Q1: Explicitly states variation? NO
      → Result: XS (1 point) - This is Roles/Permissions, not variability ✅
    
    - "Dashboard supports multiple periods (month, quarter, year)"
      → Q1: Explicitly states variation? NO (this is a filter/option)
      → Result: XS (1 point) - This is Interface Elements, not variability ✅
    
    - "No mention of variations"
      → Q1: Explicitly states variation? NO
      → Result: XS (1 point) ✅
    
    - "System supports multiple configurations"
      → Q1: Explicitly states variation? NO (too vague)
      → Result: XS (1 point) - Only count if specific configurations are mentioned ✅

- **Detailed Evaluation:** Assess based on:
    - **Variability Identification:** Are variabilities clearly identified and explicitly stated?
    - **Variation Conditions:** Are conditions for variations clearly defined?
    - **Complexity:** Number and complexity of variabilities

- **BCP Points Calculation:** Calculate points based on number and complexity of variabilities:
    - No variabilities mentioned or simple configuration: XS=1 point
    - Simple variabilities (1-2 variations with basic conditions, explicitly stated): S=2 points
    - Moderate variabilities (3-4 variations with conditional logic, explicitly stated): M=3 points
    - Complex variabilities (5+ variations or complex conditional logic, explicitly stated): L=5 points
    - Highly complex variabilities (multiple distinct implementation paths, multi-tenant, explicitly stated): XL=8 points
    - **Examples:**
        *   XS (1 point): "No configuration variations mentioned", "Single implementation path", "No variabilities explicitly stated"
        *   S (2 points): "Feature behavior varies by user preference (2 options) - explicitly stated", "Simple A/B testing scenario - explicitly mentioned"
        *   M (3 points): "Feature varies by user type and region (3-4 combinations) - explicitly stated", "Conditional behavior based on subscription tier - explicitly mentioned"
        *   L (5 points): "Multiple distinct implementation paths - explicitly stated", "Complex conditional logic based on multiple parameters - explicitly mentioned"
        *   XL (8 points): "Multi-tenant features with significantly different behavior per tenant - explicitly stated", "Complex configuration-driven architecture - explicitly mentioned"

#### Domain Entities

- **Relevance Check:** Determine if the user story involves domain entities. If not, skip this section and set `domain_entities.relevant` to `false`.

- **Explicit Definitions:** The key factor is whether the story *explicitly defines* the domain entities involved.

- **Detailed Evaluation:** Assess based on:
    - **Entity Identification:** Are entities clearly identified?
    - **Entity Count:** Number of entities involved
    - **Entity Relationships:** Are relationships between entities defined?

- **BCP Points Calculation:** Calculate points based on quantity:
    - 1 entity: XS=1 point
    - 2-3 entities: S=2 points
    - 4-5 entities: M=3 points
    - 6-7 entities: L=5 points
    - More than 7 entities: XL=8 points
    - **Examples:**
        *   XS (1 point): "Update user profile entity only", "Single table/model modification"
        *   S (2 points): "Order and OrderItem entities", "Customer and Address entities"
        *   M (3 points): "Customer, Order, OrderItem, Payment, ShippingAddress (4-5 entities)"
        *   L (5 points): "Full e-commerce domain with 6-7 related entities", "Complex domain model with multiple aggregates"
        *   XL (8 points): "Complete ERP module with extensive entity network (8+ entities)", "Enterprise-scale entity relationships"

#### New Domain Entities

- **Relevance Check:** Determine if the user story involves new domain entities (entities that don't exist yet). If not, skip this section and set `new_domain_entities.relevant` to `false`.

- **Explicit Definitions:** The key factor is whether the story *explicitly defines* the new entities to be created.

- **New Domain Entities - Identification Keywords:**
    - Look for explicit mentions of creating new entities:
      * "Criar nova entidade", "Create new entity", "Adicionar novo modelo", "Add new model"
      * "Introduzir conceito de", "Introduce concept of", "Nova tabela", "New table"
      * "Criar entidade X", "Create entity X", "Nova entidade Y", "New entity Y"
    - Differentiate between:
      * **Using existing entity** (Article, User, Order) → Count in Domain Entities, NOT New Domain Entities
      * **Creating new entity** (Review, Collection, SavedSearch) → Count in New Domain Entities
    - If story mentions operations on existing entities (create article, update user) but doesn't mention creating NEW entity types → NOT New Domain Entities
    - Only count when story explicitly states creating a NEW entity type that doesn't exist yet

- **Detailed Evaluation:** Assess based on:
    - **New Entity Identification:** Are new entities clearly identified and explicitly mentioned?
    - **New Entity Count:** Number of new entities explicitly mentioned
    - **Entity Definition:** Are new entities well-defined?

- **BCP Points Calculation:** Calculate points based on quantity:
    - Add new attributes or relationships for up to 3 existing entities: M=3 points
    - Add to business context up to 3 new entities: L=5 points
    - **Examples:**
        *   M (3 points): "Adding new fields to User, Customer, and Order entities", "Schema evolution of existing domain", "Extending current entities with new attributes"
        *   L (5 points): "Introducing Subscription, Plan, and Billing entities to existing system", "Creating new aggregates", "New domain concepts introduction", "Criar entidade Review para revisões", "Create new entity SavedSearch for saved searches"

#### Background Processes

- **Relevance Check:** Determine if the user story involves background processes (asynchronous processes, scheduled tasks, etc.). If not, skip this section and set `background_processes.relevant` to `false`.

- **Explicit Definitions:** The key factor is whether the story *explicitly defines* the background processes involved.

- **Background Processes - Clarification:**
    - **Event-driven (M=3 points):** Process triggered by a system event (order approved → send notification, user registered → send welcome email)
      * Triggered by events that occur in the system
      * Reactive processes that respond to system state changes
    - **Scheduled (L=5 points):** Time-based background jobs (daily report, monthly billing, periodic data sync)
      * Triggered by time/schedule, not by events
      * Runs on a schedule (daily, weekly, monthly, etc.)
    - **NOT background processes:**
      * Synchronous operations (immediate responses to user actions)
      * User-triggered actions that complete immediately
      * Operations that happen as part of the main user flow
    
    **MANDATORY BINARY DECISION TREE - Answer these questions in order:**
    1. **Is this process triggered by a SYSTEM EVENT (not a direct user action)?**
       □ YES → Continue to question 2
       □ NO → Go to question 3
    
    2. **Does the process happen ASYNCHRONOUSLY (not blocking the user action)?**
       □ YES → Event-driven background process → M (3 points)
       □ NO → NOT a background process → 0 points
    
    3. **Is this process triggered by TIME/SCHEDULE (daily, weekly, monthly, etc.)?**
       □ YES → Scheduled background process → L (5 points)
       □ NO → Continue to question 4
    
    4. **Does this happen IMMEDIATELY as part of the main user flow?**
       □ YES → NOT a background process → 0 points
       □ NO → Re-evaluate: Is it really a background process? If unsure, default to 0 points
    
    **Examples with decision tree:**
    - "Send email after registration"
      → Q1: Triggered by system event (registration)? YES
      → Q2: Happens asynchronously? YES
      → Result: Event-driven (M=3 points) ✅
    
    - "Display results immediately"
      → Q1: Triggered by system event? NO
      → Q3: Triggered by time/schedule? NO
      → Q4: Happens immediately as part of user flow? YES
      → Result: NOT background process (0 points) ✅
    
    - "Process payment when user clicks submit"
      → Q1: Triggered by system event? NO (triggered by user click)
      → Q3: Triggered by time/schedule? NO
      → Q4: Happens immediately as part of user flow? YES
      → Result: NOT background process (0 points) ✅
    
    - "Daily report generation"
      → Q1: Triggered by system event? NO
      → Q3: Triggered by time/schedule? YES (daily)
      → Result: Scheduled (L=5 points) ✅

- **Detailed Evaluation:** Assess based on:
    - **Process Identification:** Are processes clearly identified as background processes?
    - **Process Type:** Event-driven vs. scheduled
    - **Process Count:** Number of processes

- **BCP Points Calculation:** Calculate points based on complexity and count:
    - Process triggered by a system event (event-driven, reactive): M=3 points
    - Scheduled process (time-based background jobs): L=5 points
    - **Examples:**
        *   M (3 points): "Send notification when order is approved", "Credit evaluation when all approvals are complete", "Event-driven background jobs", "Send email after user registration"
        *   L (5 points): "Daily report generation scheduled job", "Monthly billing process", "Time-based background jobs with scheduling", "Weekly data synchronization"

#### Notifications

- **Relevance Check:** Determine if the user story involves notifications (emails, SMS, push notifications, etc.). If not, skip this section and set `notifications.relevant` to `false`.

- **Explicit Definitions:** The key factor is whether the story *explicitly defines* the notifications and their triggers.

- **Detailed Evaluation:** Assess based on:
    - **Notification Type:** Type of notification (email, SMS, push, etc.)
    - **Notification Count:** Number of notifications
    - **Trigger Definition:** Are triggers clearly defined?

- **BCP Points Calculation:** Calculate points based on count:
    **CRITICAL: Count notification TYPES, not notification DETAILS or RECIPIENTS**
    
    **MANDATORY COUNTING RULES:**
    1. **Identify all notification TYPES** explicitly mentioned in the story:
       - Email = 1 type
       - SMS = 1 type
       - Push notification = 1 type
       - In-app notification = 1 type
       - Other types (WhatsApp, Slack, etc.) = 1 type each
    
    2. **DO NOT count:**
       - Multiple recipients of the same type (email to admin + email to user = 1 type, not 2)
       - Notification content/details (subject, body, fields) as separate notifications
       - Different triggers for the same type (email on event A + email on event B = 1 type, not 2)
    
    3. **Calculate points based on number of distinct TYPES:**
       - 1 notification type: XS=1 point
       - 2-3 notification types: S=2 points
       - 4+ notification types: M=3 points
    
    **Examples:**
    - "Email to admin with DOI, Title, Name, Date" → 1 type (email) = XS (1 point) ✅
    - "Email to admin + In-app notification to user" → 2 types (email + in-app) = S (2 points) ✅
    - "Email to admin, researcher, and reviewer" → 1 type (email, multiple recipients) = XS (1 point) ✅
    - "Email to admin + SMS to user + Push notification" → 3 types = S (2 points) ✅
    - "Email on registration + Email on approval" → 1 type (email, different triggers) = XS (1 point) ✅

#### Audits

- **Relevance Check:** Determine if the user story involves audits (logging, tracking, audit trails, etc.). If not, skip this section and set `audits.relevant` to `false`.

- **Explicit Definitions:** The key factor is whether the story *explicitly defines* what needs to be audited.

- **Detailed Evaluation:** Assess based on:
    - **Audit Type:** Type of audit (logging, tracking, etc.)
    - **Audit Count:** Number of audit requirements
    - **Audit Detail:** Level of detail required

- **BCP Points Calculation:** Calculate points based on count:
    **CRITICAL: 1 Audit Requirement = 1 Point (XS)**
    - One audit requirement can track multiple fields (who, when, what, IP, action, entity ID, etc.)
    - These fields are PART OF the same audit requirement, not separate audits
    - Only count as multiple audits if there are DIFFERENT TYPES of audit requirements:
      * Example: Access audit requirement (1 point) + Modification audit requirement (1 point) = 2 points (S)
      * Example: Audit requirement tracking who, when, what, IP for article creation = 1 point (XS) - all fields are part of the same audit
    - **WRONG:** "Audit with 4 fields (who, when, what, IP) = 4 points" ❌
    - **CORRECT:** "Audit requirement for article creation tracking who, when, what, IP = 1 point" ✅
    
    Scoring:
    - 1 simple audit requirement (regardless of how many fields it tracks): XS=1 point
    - 2-3 different audit requirements (different types/purposes): S=2 points
    - 4+ different audit requirements (different types/purposes): M=3 points
    
    **Examples:**
    - "Register log with: ID do artigo, ID do usuário, Data/hora, IP, Ação" → 1 audit requirement = XS (1 point)
    - "Access audit + Modification audit" → 2 different audit requirements = S (2 points)
    - "Audit for login + Audit for data access + Audit for data modification" → 3 different audit requirements = S (2 points)

## User Story to Evaluate

{{input.key}}

{{input.summary}}

{{input.description}}

## Output Format

Return the result as a valid JSON object with ONLY the 10 functional BCP dimensions.

```json
{
  "summary": "<one sentence describing the overall functional complexity>",
  "items": [
    "Business Rules: <N rules identified, individual scores> — <total> pts",
    "Interface Elements: <N static + N dynamic, grouping calculation> — <total> pts",
    "Boundaries: <boundary type selected, reason for selection> — <points> pts",
    "Roles/Permissions: <description or not relevant> — <points> pts",
    "Solution Variabilities: <description or not relevant> — <points> pts",
    "Domain Entities: <N entities> — <points> pts",
    "New Domain Entities: <description or not relevant> — <points> pts",
    "Background Processes: <description or not relevant> — <points> pts",
    "Notifications: <N types> — <points> pts",
    "Audits: <N requirements> — <points> pts"
  ],
  "dimension_business_rules": 10,
  "dimension_interface_elements": 16,
  "dimension_boundaries": 5,
  "dimension_roles_permissions": 0,
  "dimension_solution_variabilities": 1,
  "dimension_domain_entities": 2,
  "dimension_new_domain_entities": 0,
  "dimension_background_processes": 0,
  "dimension_notifications": 0,
  "dimension_audits": 0,
  "details": {
    "business_rules":         { "relevant": true,  "example_quality": "good", "assessment": "<detailed explanation referencing BCP literature>", "detailed_explanation": "<per-rule breakdown with individual scores and sum>" },
    "interface_elements":     { "relevant": true,  "example_quality": "good", "assessment": "<detailed explanation>", "detailed_explanation": "<step-by-step grouping calculation: Group 1 (N elements) = X pts, Group 2 (N elements) = X pts, Total = X pts>" },
    "boundaries":             { "relevant": true,  "example_quality": "good", "assessment": "<detailed explanation>", "detailed_explanation": "<which boundary was selected as most complex and why>" },
    "roles_permissions":      { "relevant": false, "example_quality": null,   "assessment": "", "detailed_explanation": "not relevant" },
    "solution_variabilities": { "relevant": true,  "example_quality": "good", "assessment": "<detailed explanation>", "detailed_explanation": "<decision tree result>" },
    "domain_entities":        { "relevant": true,  "example_quality": "good", "assessment": "<detailed explanation>", "detailed_explanation": "<entity count and names>" },
    "new_domain_entities":    { "relevant": false, "example_quality": null,   "assessment": "", "detailed_explanation": "not relevant" },
    "background_processes":   { "relevant": false, "example_quality": null,   "assessment": "", "detailed_explanation": "not relevant" },
    "notifications":          { "relevant": false, "example_quality": null,   "assessment": "", "detailed_explanation": "not relevant" },
    "audits":                 { "relevant": false, "example_quality": null,   "assessment": "", "detailed_explanation": "not relevant" }
  }
}
```

Important notes:
- If a dimension is not relevant, set its `dimension_*` field to 0.
- **For Business Rules:** sum all individual rule scores — total can exceed 8.
- **For Interface Elements:** sum all group scores — there is NO maximum limit.
- **For Boundaries:** select only the most complex boundary — do NOT sum.
- All string values must be enclosed in double quotes. Do not include quotation characters inside string values.
- Return only the JSON object, no explanation or additional text.
