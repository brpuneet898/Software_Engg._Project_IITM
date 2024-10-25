import google.generativeai as genai
import os
from pinecone import Pinecone
from transformers import AutoTokenizer, AutoModel
import torch

genai.configure(api_key="AIzaSyB7t4BLUq7lmE-7Es7GGRsTCcNUKULSfPg")
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

from html import escape


def get_response_key(question):
    response = gemini_model.generate_content(question)
    return response.text

def get_response(question):
    response = gemini_model.generate_content(question)
    response_text = response.text

    # Escape any HTML special characters
    escaped_text = escape(response_text)

    # Convert markdown-like syntax to HTML with precise formatting
    html_text = markdown_to_html(escaped_text)

    return html_text

def markdown_to_html(text):
    """Convert markdown-like text to HTML with proper formatting."""
    # Convert headers with specific font size and remove extra colons
    text = text.replace("Student Analysis:", "<h2 style='font-size: 14pt; margin-bottom: 10px;'>Student Analysis </h2>")
    text = text.replace("Strengths:", "<h3 style='font-size: 14pt; margin-bottom: 8px; margin-top:8px;'>Strengths</h3>")
    text = text.replace("Weaknesses:", "<h3 style='font-size: 14pt; margin-bottom: 8px;margin-top:8px;'>Weaknesses</h3>")
    text = text.replace("Actionable Feedback:", "<h3 style='font-size: 14pt; margin-bottom: 8px;margin-top:8px;'>Actionable Feedback</h3>")
    text = text.replace("Overall:", "<h3 style='font-size: 14pt; margin-bottom: 8px;margin-top:8px;'>Overall</h3>")

    # Convert symbols to whitespace and remove unwanted characters
    text = text.replace("**", " ").replace("*", " ").replace("#", " ")
    text = text.replace("& x27;", "'")  # Correct single quotes encoding

    # Convert list items and minimize spacing
    lines = text.split('\n')
    formatted_lines = []
    for line in lines:
        if line.strip().startswith("-"):
            formatted_lines.append(f"<li style='margin-bottom: 5px;margin-top:5px'>{line.strip()[1:].strip()}</li>")
        else:
            formatted_lines.append(line.strip())

    text = "\n".join(formatted_lines)

    # Wrap lists in unordered list tags
    if "<li>" in text:
        text = text.replace("<li>", "<ul style='margin-left: 20px;'><li>").replace("</li>", "</li></ul>")

    # Apply Times New Roman font and ensure proper spacing
    html_content = (
        "<div style='font-family: \"Times New Roman\", Times, serif; font-size: 12pt; line-height: 1.5;'>"
        + text
        + "</div>"
    )

    return html_content


# Load the multilingual-e5-large model and tokenizer from Huggingface
tokenizer = AutoTokenizer.from_pretrained("intfloat/multilingual-e5-large")
model = AutoModel.from_pretrained("intfloat/multilingual-e5-large")

# Function to generate embeddings
def generate_embedding(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        embeddings = model(**inputs)
    return embeddings.last_hidden_state.mean(dim=1).squeeze().numpy()

def make_prompt(query, relevant_passage):
  escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
  prompt = ("""You are a helpful and informative bot that answers questions using text from the reference passage included below. \
  Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. \
  However, you are talking to a non-technical audience, so be sure to break down complicated concepts and \
  strike a friendly and converstional tone. \
  If the passage is irrelevant to the answer, you may ignore it. Ensure that you still attempt to answer the question to you maximum ability. Do not mention the use of the passage to me.\
  Important Note : Provide HTML Friendly Answers,Formatted. \
  QUESTION: \n'{query}'
  PASSAGE: '{relevant_passage}'

    ANSWER:
  """).format(query=query, relevant_passage=escaped)

  return prompt


# Initialize Pinecone
api_key = "0208c975-9131-40cb-97ca-998b8aebbe51"
pc = Pinecone(api_key=api_key)
index = pc.Index("iitm-transcripts")


# Function to fetch context from Pinecone
def fetch_context(query, top_k=10):
    # Generate embedding for the query
    query_embedding = generate_embedding(query)  # Use the same function to generate embedding

    # Query Pinecone
    results = index.query(
        vector=query_embedding.tolist(),
        top_k=top_k,
        include_metadata=True,
        namespace="ns1"
    )

    # Extract and return the context
    context = " ".join([ result['metadata']['transcript'] for result in results['matches']])
    return context

# Example usage

def full_fucntion(question):
    context = fetch_context(question)
    prompt = make_prompt(question, context)
    answer = get_response(prompt)
    return answer.text



def get_summary(transcript):
    prompt = ("""You are a helpful and informative bot that sumarizes text and transcripts provided to you below namely the passage. \
    Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. \
    However, you are talking to a non-technical audience, so be sure to break down complicated concepts and \
    strike a friendly and converstional tone. \
    Refer to the passage below as "the lecture". \
    Important Note : Provide HTML Friendly Answers,Formatted. \
    QUESTION: \n'Summarize the passage below'
    PASSAGE: '{transcript}'

        ANSWER:
    """).format( transcript=transcript)
    summary = get_response(prompt)
    return summary

def get_key(transcript):
    prompt = ("""You are a helpful and informative bot that analyzes text and transcripts provided to you below namely the passage and from these generates the key topics discussed in the video. \
    Respond in short bullet points each on a new line in a markdown format. \
    Be very concise and to the point. \
    Ensure that you add a line break after each bullet point. \
    QUESTION: \n'Extract key points and topics covered from the passage below'
    PASSAGE: '{transcript}'

        ANSWER:
    """).format(transcript=transcript)
    
    # Get the response (which is already a string)
    key = get_response_key(prompt)
    
    # Split the key points using newlines first
    key_points = key.split('\n')
    
    # Remove leading hyphens and extra spaces
    key_points = [point.lstrip('- ').strip() for point in key_points if point.strip()]
    
    # Format the key points as an unordered list
    formatted_key_points = '<ul>\n' + '\n'.join([f'<li>{point}</li>' for point in key_points]) + '\n</ul>'
    
    return formatted_key_points



all_asg = {
  1:{
      
    1:
      [
        "",
        {
            1:[ "Software can be divided into manageable components. Find the one(s) that are TRUE about breaking software into components from the list below. ", 
                ["It is a way of breaking the complexity of the system into manageable parts.","It enables different teams to work on different components.", "veryone on the development team must know how to work with all the components.", "It conceals implementation details while providing an interface for others to display its capabilities."], 
                ["It is a way of breaking the complexity of the system into manageable parts.", "It enables different teams to work on different components.","It conceals implementation details while providing an interface for others to display its capabilities."] 
              ],    

        }
      ],



      2:
      [
        "",
        {
            1:[ "A software company wants to build a website for employee wellfare to cater services to its own employees, and thus requires to interact with the employees from different departments. In this case which type of clients are we dealing with?", 
                ["external users","internal users", "software or software components", "developers"], 
                ["internal users"] 
              ]
        }
      ],


      

      3:
      [
        "",
        {
            1:[ "Presently a lot of software development takes place in a distributed environment, the developer is expected to write precise interface definitions. From the given options, which is/are TRUE about interface definition.", 
                ["It describes the capabilities of a function.","It provides the implementation details of a function.", "It tells which requests are allowed and specifies the format of the output.", "he code implementing the interface should remain unchanged for a given interface definition."], 
                ["It describes the capabilities of a function.", "It tells which requests are allowed and specifies the format of the output."] 
              ]
        }
      ],    



      4:
      [
        "",
        {    
            1:[ "Which of the following tests ensures that the requirements given by the clients are actually met?", 
                ["Unit testing","Modular testting", "Integration testing", "Acceptence testing"], 
                ["Acceptence testing"] 
              ]
        }
      ],
    

      5:
      [
        "",
        {    
            1:[ "The acceptance testing conducted by a group of selected end users in a real-live environment is called _______", 
                ["Unit testing","Integration testing", "Alpha testing", "Beta testing"], 
                ["Beta testing"] 
              ]
        }
      ],
    
      6:
      [
        "",
        {    
            1:[ "Consider X is a software developer working in a renowned software company. X is given responsibility to develop a particular component of a big software. After finishing the coding X wants to test the developed component. Identify the type of testing X wants to perform.", 
                ["Unit testing","Integration testing", "Alpha testing", "Beta testing"], 
                ["Unit testing"] 
              ]
        }
      ],
    
      7:
      [
        "",
        {    
            1:[ "Which of the following are the disadvantages of using waterfall model?", 
                ["It is not suitable if client requirements are unclear or client is not sure about the entire requirement.","Building prototype results in extra cost which is usually discared afterwards.", "Any change request is made after the requirement gathering phase is completed results in significant increase in cost and time", "The clients gets first view of the product very late compared to other SDLC models."], 
                ["It is not suitable if client requirements are unclear or client is not sure about the entire requirement.", "Any change request is made after the requirement gathering phase is completed results in significant increase in cost and time", "The clients gets first view of the product very late compared to other SDLC models."] 
              ]
        }
      ],
    
      8:
      [
        "",
        {    
            1:[ "An EdTech company got a contract to build an E-learning system for a school. It decides to first focus on the key feature that the school requires - i.e. to create an online attendance module. The team develops, tests and delivers this module to the school, and then starts working on the next module. The software development process followed in this case is similar to", 
                ["Waterfall model","V-model", "Prototype model", "Agile model"], 
                ["Agile model"] 
              ]
        }
      ],

      9:
      [
        "",
        {    
            1:[ "Which of the following statements are true?", 
                ["Description of what your functions can do without describing the implementation in detail is known as an interface.","The code implemented by the interface cannot change once it has been designed.", "The code implemented by the interface can change once it has been designed."], 
                ["Description of what your functions can do without describing the implementation in detail is known as an interface.","The code implemented by the interface can change once it has been designed."] 
              ]
        }
      ], 

      10:
      [
        "A software company wants to develop a website http://www.slightest.com/, that, given a product's details, queries different e-shopping websites and recommends the website that provides the product at the lowest cost. Consider the following tasks, which are performed to build this website, map them to the appropriate phase in the software development process.",
        {    
            1:[ "The company designed a set of questions to conduct a survey on how customers want to search for a product and what details they want to provide.", 
                ["Requirement gathering","Development phase", "Design phase", "Testing phase","Maintenence phase"], 
                ["Requirement gathering"] 
            ],
            2:[ "The entire task is divided into different modules, and the interactions between the modules are outlined.", 
                ["Requirement gathering","Development phase", "Design phase", "Testing phase","Maintenence phase"],  
                ["Design phase"] 
            ],
            3:[ "Different teams of the developers start coding their assigned modules.", 
                ["Requirement gathering","Development phase", "Design phase", "Testing phase","Maintenence phase"], 
                ["Development phase"] 
            ],
            4:[ "The link to the website is given to a predefined set of customers. The customer uncovered an error that if more than one e-shopping website provided the minimum price, then only one of them would be shown by the website.", 
                ["Requirement gathering","Development phase", "Design phase", "Testing phase","Maintenence phase"], 
                ["Testing phase"] 
            ],
            5:[ "Following the final release of http://www.slightest.com/, a large number of customers requested that the delivery time of the product be included as a search criteria alongside the price. The developer company decided to proceed with the change.", 
                ["Requirement gathering","Development phase", "Design phase", "Testing phase","Maintenence phase"], 
                ["Maintenence phase"] 
            ],                                
        }
      ],  
  },
  2:{
  
    1:
        [
        "A healthcare smartwatch has to be developed for COVID19 patients so that if the device identifies any risks associated with the patient's health condition, it alerts the shift doctors to take preventive measures. Doctors will provide the requirements for this system. For the following given questions identify the type of problem in the given requirement.",
        {
            1:[ "A doctor specifies that if the body temperature is more than 104 F, the doctor should be alerted. However, the actual requirement is that if the body temperature is more than 104 F and the oxygen saturation level is less than 92%, then only the device must alert the doctor.", 
                ["Ambiguous","Inconsistency", "Incompleteness", "None of above"], 
                ["Incompleteness"] 
                ],    
            2:[ "A doctor specifies that if the oxygen saturation level is too low, the device must alert the doctor.", 
                ["Ambiguous","Inconsistency", "Incompleteness", "None of above"], 
                ["Ambiguous"] 
                ], 
            3:[ "Doctor-1 specifies that if the body temperature is more than 104 F, the doctor should be alerted. Doctor-2 specifies that if the body temperature is more than 103 F and the oxygen saturation level is less than 92%, then only the device must alert the doctor.", 
                ["Ambiguous","Inconsistency", "Incompleteness", "None of above"], 
                ["Inconsistency"] 
                ],                 

        }
        ],
    
    
    2:
        [
        "",
        {
            1:[ "Identify the type of requirement collection technique used when it is required to achieve some consensus about the requirements and also highlight the areas of conflict.", 
                ["Questionnaires","Interviews", "Focus group","Documentations"], 
                ["Focus group"] 
                ],    

        }
        ],
    
    3:
        [
        "",
        {
            1:[ "An organisation decided to develop an online medicine selling app. So a team from the organisation visited some medical shops to observe the process of selling the medicines. Identify the type of requirement collection technique used in the given scenario.", 
                ["Questionnaires", "Focus group","Naturalistic observations","Documentations"], 
                ["Naturalistic observations"] 
                ],    

        }
        ], 
    
        4:
        [
        "",
        {
            1:[ "A software company has to develop a portal that enables a user to search for a specific product by providing some product details. The portal queries and gathers details from different websites and puts them together on a single page. Consider the following two requirements: Requirement 1: The portal must gather information for the given product from all the relevant websites and display it to the user. Requirement 2: Given the product details, the portal must complete the gathering and display of information within 10 secs. Which of the following statement is true?", 
                ["Requirement 1 is a functional requirement, whereas Requirement 2 is a non-functional requirement.", "Requirement 2 is a functional requirement, whereas Requirement 1 is a non-functional requirement.","Both requirements are functional requirements.","Both the requirements are non-functional requirements."], 
                ["Requirement 1 is a functional requirement, whereas Requirement 2 is a non-functional requirement."] 
                ],    

        }
        ], 
    
    5:
        [
        "Consider the user story given below for a food delivery app and answer the following questions. Feature 1: Search dishes. As a customer, I want to search for a dish so that I can get the description of the dish along with its price and estimated delivery time within a reasonable time. The results must be displayed with appropriate pagination and filters.",
        {
            1:[ "The statement: 'I want to search for a dish' reflects which component of the role-feature-benefit template of the user story?", 
                ["an action","a benefit", "type of user"], 
                ["an action"] 
                ],    
            2:[ "The statement: 'so that I can get the description of the dish along with its price and estimated delivery time within a reasonable time' reflects which component of the role-featurebenefit template of the user story?", 
                ["an action","a benefit", "type of user"], 
                ["a benefit"] 
                ],  
            3:[ "Consider the following improvement in the user story. The statement 'As a customer, I want to search for a dish' is modified as: 'As a customer, I want to search for a dish by specifying the dish by name or by the main ingredients used' It makes the user story more ____. ", 
                ["Specific","Measurable", "Achievable", "Relevant","Timeboxed"], 
                ["Specific"] 
                ],  
            4:[ "Consider the following improvement in the user story. The statement 'so that I can get the description of the dish along with its price and estimated delivery time within a reasonable time. The results must be displayed with appropriate pagination and filters.' is modified as: 'so that I can get the description of the dish along with its price and estimated delivery time within 2 seconds. The results must be displayed with appropriate pagination and filters.' It makes the user story more ____.", 
                ["Specific","Measurable", "Achievable", "Relevant","Timeboxed"],  
                ["Measurable"] 
                ],  
            5:[ " It has been found that implementation of Feature 1 is not possible within one agile iteration. Feature 1: Search dishes. Thus the Feature 1 is subdivided as follows: Feature 1a: Search and display dishes within a single page. Feature 1b: Add pagination and filters, It makes the user story more ____.", 
                ["Specific","Measurable", "Achievable", "Relevant","Timeboxed"],  
                ["Achievable"] 
                ],  
            6:[ "The implementation of Feature 1 has been stopped since the time and budget exceeded and the organization has decided to reschedule for the portions left. It makes the user story more ____.", 
                ["Specific","Measurable", "Achievable", "Relevant","Timeboxed"],   
                ["Timeboxed"] 
                ],                                          

        }
        ],
  },
  3:{

    1:
        [
        "",
        {
            1:[ "Consider an operating system that asks users if they really want to delete every time they try to delete a file or folder. Which of the following usability goals is fulfilled by the operating system?",
                ["Effectiveness","Efficiency","Safe to use","Learnability","Memorability"],
                ["Safe to use"]
                ],

        }
        ],

    2:
        [
        "",
        {
            1:[ "An employee payroll software provides its users with several services. For each service, a tutorial video is provided along with step-by-step examples. Which of the following usability goals is fulfilled by the payroll software?",
                ["Effectiveness","Efficiency","Safe to use","Learnability","Memorability"],
                ["Learnability"]
                ],

        }
        ],

    3:
        [
        "",
        {
            1:[ ". ",
                ["Effectiveness","Efficiency","Safe to use","Learnability","Memorability"],
                ["Safe to use"]
                ],

        }
        ],

    4:
        [
        "",
        {
            1:[ ". ",
                ["Effectiveness","Efficiency","Safe to use","Learnability","Memorability"],
                ["Safe to use"]
                ],

        }
        ],

    5:
        [
        "",
        {
            1:[ "Assume one of the apps on your mobile phone enables you to do a bulk download of files from Google Drive. The app has a feature that if the storage of your mobile is 90% full, then it shows an alert message and prompts you to clear some amount of storage space. Which of the following heuristics of UI evaluation is satisfied by the app?",
                ["Prevent errors","Show status","Support error recovery","Provide help"],
                ["Show status"]
                ],

        }
        ],

    6:
        [
        "",
        {
            1:[ "A given prototype is a hand-drawn comic that features the setting, sequence, and satisfaction. Identify the type of the given prototype.",
                ["Storyboards","Paper prototype","Digital mock-ups","Interactive prototype"],
                ["Storyboards"]
                ],

        }
        ],

    7:
        [
        "",
        {
            1:[ "A food delivery app allows a user to place an order with a minimum number of clicks. It also remembers the favourite dishes of a user along with the delivery address and payment information. Which of the following usability goals is fulfilled by the mobile app?",
                ["Effectiveness","Efficiency","Safe to use","Learnability","Memorability"],
                ["Efficiency"]
                ],

        }
        ],

    8:
        [
        "",
        {
            1:[ "Which of the following belong to users experience goals?",
                ["motivating","effective and efficient","satisfying","safe and less error-prone","entertaining","durable"],
                ["motivating","satisfying","entertaining"]
                ],

        }
        ],

    9:
        [
        "",
        {
            1:[ "Which of the following prototype is the closest to the final product?",
                ["Storyboards","Paper prototype","Digital mock-ups","Interactive prototype"],
                ["Interactive prototype"]
                ],

        }
        ],

    10:
        [
        "",
        {
            1:[ "When developing software to create and edit spreadsheets, you give regular users a menu-based interface and give advanced users shortcuts to perform different tasks. Which of the following heuristics of UI evaluation is fulfilled in this case?",
                ["Flexibility","Consistency","Clean and functional design","Freedom"],
                ["Flexibility"]
                ],

        }
        ],

    11:
        [
        "",
        {
            1:[ "You are designing a web page for user registration where a user can upload his/her image, it also shows a progress bar to show the upload status. Which of the following heuristics of UI evaluation is satisfied in this case?",
                ["Prevent errors","Show status","Support error recovery","Provide help"],
                ["Show status"]
                ],

        }
        ],

    12:
        [
        "",
        {
            1:[ "An organisation uses an app to register all new employees in the organization. During the registration, the new employee has to select his/her joining date from a calendar shown on the interface. The calendar disables selection of all the dates that fall on a weekends or on an official holiday declated by the organization. Which of the following heuristics of UI evaluation is satisfied by the app?",
                ["Prevent errors","Show status","Support error recovery","Provide help"],
                ["Prevent errors"]
                ],

        }
        ],
  },
  4:{

    
    1:
      [
        "",
        {
            1:[ "A project requires 240 person-months of development time. Which of the following statements is/are true?",
                ["It requires 240 developers to complete the project.","It requires 10 developers to complete the project in 2 years.", "It requires 120 developers to complete the project in 2 months.","It requires 24 developers to complete the project in 10 years."],
                ["It requires 10 developers to complete the project in 2 years.", "It requires 120 developers to complete the project in 2 months."]
              ],

        }
      ], 


    2:
      [
        "",
        {
            1:[ "Consider the following statements: Statement 1: Project estimation is based on the experience of the people who have completed similar types of projects. Statement 2: Project estimation is based on mathematical models. Select the option that is correct about the above statements.         ",
                ["Both Statement 1 and Statement 2 are true for Empirical estimation techniques.","Both Statement 1 and Statement 2 are false for Heuristic estimation techniques", "Statement 1 is true for Empirical estimation techniques and Statement 2 is true for Heuristic estimation techniques","Statement 1 is true for Heuristic estimation techniques and Statement 2 is true for Empirical estimation techniques."],
                ["Statement 1 is true for Empirical estimation techniques and Statement 2 is true for Heuristic estimation techniques"]
              ],

        }
      ],
    
    3:
      [
        "",
        {
            1:[ "A software company wants to develop a mobile app to beatify the snaps taken by mobile cameras. The company wants to estimate the cost of the product. Therefore, they have developed a team comprising a group of experts (estimators) and a co-ordinator. First, the coordinator provides each estimator with a copy of SRS and a form for recording his or her estimation. Each estimator estimates the cost and anonymously submits the form to the coordinator. The coordinator compiles a summary of these responses and publishes it. The entire process is repeated several times. What kind of estimation technique is used in the given scenario? ",
                ["Expert judgement","Delphi technique", "COCOMO estimation model","None of the above"],
                ["Delphi technique"]
              ],

        }
      ],
    
    4:
      [
        "",
        {
            1:[ "A software company must develop a smartwatch that can continuously monitor several health parameters of the customer wearing it. The development team has to build software that would be strongly coupled with the hardware of the smartwatch. The values for the constants in the COCOMO model for the different types of the project are as follows: Organic project: a = 2.4, b = 1.05 Semi-organic project: a = 3.0, b = 1.12 Embedded project: a = 3.6, b = 1.20 Considering the source code of 50,000 lines and effort adjustment factor = 1.62, what is the final estimated effort for the project?        ",
                ["394","146", "240","638"],
                ["638"]
              ],

        }
      ],
    
    5:
      [
        "",
        {
            1:[ "In the given WBS, Requirement gathering and analysis is ___.",
                ["the project name","an activity which can be further breakdown into smaller task", "a task which can be allocated to a developer and scheduled","None of the above"],
                ["an activity which can be further breakdown into smaller task"]
              ],

        }
      ],
    
    6:
      [
        "Consider that a software company is developing an e-shopping application. However, it has been found that most of the developer team members do not have sufficient domain knowledge",
        {
            1:[ "Identify the type of risk in the given scenario.",
                ["Technical risk","Project risk", "Business risk","None of above"],
                ["Project risk"]
              ],

        }
      ],
    
    7:
      [
        "",
        {
            1:[ "Select the correct option that specifies how the risk can be mitigated.",
                ["By communicating with clients or building prototype to collect clients' feedback","By benchmarking and regular inspection to verify that the external component is up to the mark.", "By hiring developers with relevant experience within the company and/or outside the company.","By training multiple people with the required skills to work on the project"],
                ["By hiring developers with relevant experience within the company and/or outside the company."]
              ],

        }
      ],
    
    8:
      [
        "",
        {
            1:[ "Consider that a software company is developing an e-shopping application. However, the project has exceeded the estimated budget. Identify the type of risk in the given scenario.",
                ["Technical risk","Project risk", "Business risk","None of above"],
                ["Project risk"]
              ],

        }
      ],
    9:
      [
        "Consider that a software company is developing an editor to process text documents. However, the editor has been found not competitive in the market.",
        {
            1:[ "Identify the type of risk in the given scenario.",
                ["Technical risk","Project risk", "Business risk","None of above"],
                ["Business risk"]
              ],
            2:[ "Select the correct option that specifies how the risk can be mitigated.",
                ["By communicating with clients or building prototype to collect clients' feedback","By benchmarking and regular inspection to verify that the external component is up to the mark.", "By exploring the market for similar products.","By training multiple people with the required skills to work on the project."],
                ["By exploring the market for similar products."]
              ],
        }
      ], 
  },
  5:{

    1:
      [
        "",
        {
            1:[ "When all the functions in each module of a software system perform a single objective, then the modules ________. ",
                ["Have high cohesion","Have low cohesion", "Are highly coupled", "Are lowly coupled"],
                ["Have high cohesion"]
              ],

        }
      ],
    2:
      [
        "",
        {
            1:[ "A software design process has ensured that the changes to the software will be easy to implement even after the product has been released. Which of the following characteristics of a good software design is ensured in the above process?",
                ["Correctness","Efficiency", "Maintainability","Understandable"],
                ["Maintainability"]
              ],

        }
      ],
    3:
      [
        "",
        {
            1:[ "When function calls between two modules involve passing a large chunk of shared data, then the modules ________",
                ["Have high cohesion","Have low cohesion", "Are highly coupled", "Are lowly coupled"],
                ["Are highly coupled"]
              ],

        }
      ],
    4:
      [
        "",
        {
            1:[ "Consider a food delivery app in which the order module interacts with the payment module to initiate payment for an order by passing the payable amount (which is of floating point type). Identify the type of coupling in the given context.",
                ["Content coupling","Common coupling", "Control coupling", "Data coupling"],
                ["Data coupling"]
              ],

        }
      ],
    5:
      [
        "",
        {
            1:[ "Consider an e-commerce app in which the order module interacts with the delivery module to initiate order delivery by passing a flag indicating whether the customer is a regular customer or a priority customer. Depending on the flag value, the delivery module executes different internal logic. Identify the type of coupling in the given context. ",
                ["Content coupling","Common coupling", "Control coupling", "Data coupling"],
                ["Control coupling"]
              ],

        }
      ],
    6:
      [
        "",
        {
            1:[ "In an object-oriented design for a Library Management System, the objects of Novel class are categorised into two classes, namely objects of Fiction class and objects of Nonfiction class. Identify the class relationship between Novel class and, Fiction and Nonfiction classes. ",
                ["Association", "Composition", "Inheritance", "Dependency"],
                ["Inheritance"]
              ],

        }
      ],
    7:
      [
        "",
        {
            1:[ "In which of the following diagram models, is the flow of control among computational activities?",
                ["Class diagram", "State machine diagram", "Activity view", "Interaction view"],
                ["Activity view"]
              ],

        }
      ],
  },
  7:{

    1:
      [
        "",
        {
            1:[ "Which of the following statements about the flask framework is/are correct? ",
                ["It is a mobile application framework.","It is a web application framework.", "It is a micro-framework.", "It imposes several restrictions on developing applications, like the kind of databases that can be used and the type of web servers that can be used."],
                ["", ""]
              ],

        }
      ],
    2:
      [
        "",
        {
            1:[
                '''Consider the code given in Python.\n
                def lsearch(key, list):\n
                for i in list:\n
                if i == key:\n
                print('key found')\n
                return\n
                print('key not found')\n
                list = [10, 20, 30, 40]\n
                lsearch(40, list)\n\n
                What is the cyclomatic complexity of the function lsearch?''',
                ["1", "2", "3", "4"],
                [""]
              ],

        }
      ],
    3:
      [
        "",
        {
            1:[ "Which of the following range of cyclomatic complexities represents an error-prone, unstable code?",
                ["11 - 20","21 - 30", "31 - 40", ">=41"],
                [""]
              ],

        }
      ],
    4:
      [
        "",
        {
            1:[ "During debugging, a developer finds out the statement that generates incorrect output. He follows data and control dependencies backwards to find the incorrect line of code. Which of the following debugging strategies was chosen by the developer?",
                ["Input manipulation","Backwards strategy", "Forwards strategy", "Blackbox debugging"],
                [""]
              ],

        }
      ],
    5:
      [
        "",
        {
            1:[ "Identify the statements which are true and related to the code smells.",
                ["All the commented-out codes should be retained in the final code base.","It is better to have a function that does many things", "A function ideally should not have any argument, however, in practical situations, it should not use more than three arguments.", "A function should not use any flag (based on which function perform certain operations) argument."],
                ["", ""]
              ],

        }
      ],
    6:
      [
        "",
        {
            1:[ "Which of the following types of software metrics considers the number of distinct operators and the total number of operators along with the number of distinct operands and the total number of operands to measure various properties in a program, like a program vocabulary, difficulty, volume, etc.?",
                ["Cyclomatic complexity","Raw Metrics", "Halstead's Metrics", "None of the above"],
                [""]
              ],

        }
      ],
    7:
      [
        "",
        {
            1:[ "Consider a program that finds the minimum integer from a list of integers. For debugging purposes, the developer uses various inputs and observes the differences in output. Which of the following debugging strategies is chosen by the developer?",
                ["Input manipulation","Backwards strategy", "Forwards strategy", "Blackbox debugging"],
                [""]
              ],

        }
      ],
    8:
      [
        "",
        {
            1:[
                '''Consider the status of your local repository as given below.\n\n
                  $ git status\n
                  warning: unable to unlink '/home/db/sample/.git/index.lock': Permission denied\n
                  On branch master\n
                  Changes not staged for commit:\n
                  (use \"git add <file>...\" to update what will be committed)\n
                  (use \"git restore <file>...\" to discard changes in working directory)\n
                  modified: file1.py\n
                  Untracked files:\n
                  (use \"git add <file>...\" to include in what will be committed)\n
                  data.txt\n
                  lib/\n
                  no changes added to commit (use \"git add\" and/or \"git commit -a\")\n\n
                  The file data.txt contains 4 GB of raw data that you do not want to share with others working on the same repository. 
                  You have also modified file1.py and added a directory lib which has two files in it, this set of changes you want to share with the others. 
                  Select the most appropriate version control strategy to accomplish this.''',
                ["$ git add .\n$ git commit -m \"adding new files\"","$ git commit -ma \"adding new files\"", "$ git add lib\n$ git commit -m \"adding new library files\"", "$ git add lib file1.py\n$ git commit -m \"adding new files\""],
                [""]
              ],

        }
      ],
  },
  8:{

    1:
      [
        "",
        {
            1:[ "Consider a video editing software that enhances the quality of the videos taken by mobile cameras. The input video undergoes processing by several components of the software, and the output of one component is fed to the input of the next. Each component gradually enhances the quality of the input video. Identify the type of software architecture used for the video editing software.",
                ["Client-server system","Pipe and filter", "Model view controller", "Peer-to-peer architecture"],
                [""]
              ],

        }
      ],
    2:
      [
        "",
        {
            1:[
                "Consider developing a food delivery app that provides a catalogue of different food items. The food items are supplied by the respective restaurants. The class Restaurant is used to store information about the restaurants as well as information about the food items. Furthermore, the class Restaurant also provides functions like adding restaurants, modifying restaurants, deleting restaurants, adding food items, modifying food items, and deleting food items. Identify the SOLID principle that is violated by the class Restaurant.",
                ["Single responsibility principle","Open-close principle", "Liskov substitution principle", "Interface segregation principle", "Dependency inversion principle"],
                [""]
              ],

        }
      ],

    3:
      [
        "",
        {
            1:[ '''Consider the design of an online food delivery app. It has an interface DeliveryProcessing that specifies the methods to be implemented by any delivery class, and those are packageOrder(), notifyCustomer(), bookDeliveryPartner() and deliver().\n\n
                However, along with ordering the food, which has to be delivered physically, customers can also order to dine out. For dine-out bookings, a dine-out coupon would be delivered to the customers online.\n\n
                To support the dine-out coupon delivery process, the actual DeliveryProcessing interface is segregated into two different interfaces:\n\n
                -- interface PhysicalDeliveryProcess which provides the methods (to be implemented) to support the physical delivery of the food items for normal orders,\n\n
                -- interface CouponDeliveryProcess which provides the methods (to be implemented) to support online delivery of the coupons for dine-out booking for dine-out orders.\n\n
                Identify the SOLID principle that is fulfilled by the design.''',
                ["Single responsibility principle","Open-close principle", "Liskov substitution principle", "Interface segregation principle", "Dependency inversion principle"],
                [""]
              ],

        }
      ],
    4:
      [
        "",
        {
            1:[ "Which of the following types of design patterns ensures effective communication between the objects such that the responsibilities of the objects are well distributed?",
                ["Creational design pattern","Structural design pattern", "Behavioural design pattern", "None of the above"],
                [""]
              ],

        }
      ],


    5:
      [
        "",
        {
            1:[ "Consider an IoT-based system in a chemical plant that starts the cooling system if the temperature within the plant reaches a threshold. The class CoolerOperator can operate at all the temperatures that are given in Fahrenheit. However, some of the sensors measure temperature in Celsius and some in Kelvin. TemperatureConvertor, the class responsible for temperature conversion (Celsius to Fahrenheit and Kelvin to Fahrenheit), is incompatible with the class CoolerOperator. Which design pattern can be used to solve the problem?",
                ["Factory design pattern","Builder design pattern", "Adapter design pattern", "Facade design pattern"],
                [""]
              ],

        }
      ],

    6:
      [
        "",
        {
            1:[ "Which among the following are behavioural design patterns?",
                ["Factory design pattern","Builder design pattern", "Iterator design pattern", "Adapter design pattern", "Strategy design pattern"],
                ["", ""]
              ],

        }
      ],
  }
}


demo_results= {
    1:{
        1:"yes"
    },
    2:{
        1:"no"
    },
    3:{
        1:"yes"
    },
    4:{
        1:"no"
    },
    5:{
        1:"yes"
    },
    6:{
        1:"no"
    },
    7:{
        1:"yes"
    },
    8:{
        1:"no"
    },
    9:{
        1:"yes"
    },
    10:{
        1:"no",
        2:"no",
        3:"yes",
        4:"yes",
        5:"yes"
    },

}

def feedback_gen(asg_no, results):
    asg_number = int(asg_no)

    # Initial instructions for the AI model
    initial_instructions = (
        "<h3>You are an analyzer who analyzes student assignment submissions.</h3>"
        "<p>Based on the questions answered correctly and incorrectly, identify the student's strengths and weaknesses. "
        "Provide actionable feedback on what topics the student needs to focus on to improve, and acknowledge their strengths. "
        "Focus on both the correctness of the answers and the reasoning behind them.</p>"
    )

    # Prepare sections for correct, partially correct, and incorrect questions
    correct_questions = "<h4>Correctly Answered Questions:</h4>"
    partially_correct_questions = "<h4>Partially Correctly Answered Questions:</h4>"
    incorrect_questions = "<h4>Incorrectly Answered Questions:</h4>"

    question_counter = 0
    for group_id, questions in results.items():
        for question_id, details in questions.items():
            question_counter += 1
            question_text = all_asg[asg_number][group_id][1][question_id][0]
            correct_opts = "<br>".join(all_asg[asg_number][group_id][1][question_id][2])
            selected_opts = "<br>".join(details["selected"])

            if details["status"] == "Correct":
                correct_questions += (
                    f"<p><strong>Q{question_counter}:</strong> {question_text}<br>"
                    f"<strong>Correct Options:</strong><br>{correct_opts}<br>"
                    f"<strong>Selected Options:</strong><br>{selected_opts}</p>"
                )
            elif details["status"] == "Partially Correct":
                partially_correct_questions += (
                    f"<p><strong>Q{question_counter}:</strong> {question_text}<br>"
                    f"<strong>Correct Options:</strong><br>{correct_opts}<br>"
                    f"<strong>Selected Options:</strong><br>{selected_opts}</p>"
                )
            else:  # Incorrect
                incorrect_questions += (
                    f"<p><strong>Q{question_counter}:</strong> {question_text}<br>"
                    f"<strong>Correct Options:</strong><br>{correct_opts}<br>"
                    f"<strong>Selected Options:</strong><br>{selected_opts}</p>"
                )

    # Combine all sections into a single HTML string
    final_to_send = (
        initial_instructions + "<br>" +
        correct_questions + "<br>" +
        partially_correct_questions + "<br>" +
        incorrect_questions
    )

    # Send the prompt to the generative model
    response_gen = get_response(final_to_send)

    # Here we assume `response_gen` contains the AI-generated HTML-friendly response.
    feedback = response_gen  # The generated feedback
    raw_feedback = final_to_send  # The raw prompt sent to the model

    return feedback, raw_feedback




def individual_doubt(doubt, context, question, options, answer):
    initial_inst = (
        "You are a doubt solver who solves the doubts of the students which are based on a specific question. "
        "A student has asked you the following doubt. He has also provided the corresponding question:\n\n"
    )
    final_inst = (
        "Solve the doubt using the given information. Give the response directly to the student. "
        "Remember to not give the student the answer directly even if he asks for it. "
        "You are there to teach him, not to enable copying.\n"
        "if the student greets you, greet him back. If he thanks you, thank him back and close the conversation."
    )
    
    question_text = f"**Question:**\n{context}\n{question}\n\n"
    options_text = f"**Options:**\n" + "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)]) + "\n\n"
    answer_text = f"**Correct Answer:** {', '.join(answer)}\n\n"
    doubt_text = f"**Student's Doubt:**\n{doubt}\n\n"
    
    final_to_send = initial_inst + question_text + options_text + answer_text + doubt_text + final_inst

    cleared_doubt = get_response(final_to_send)

    # Enhance formatting for readability in HTML context
    cleared_doubt = cleared_doubt.replace('\n', '<br>').replace('*', '<strong>').replace('_', '<em>')
    
    return cleared_doubt


