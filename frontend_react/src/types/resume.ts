export interface Experience {
  id: string;
  jobTitle: string;
  companyName: string;
  startDate: string;
  endDate: string;
  description: string;
}

export interface Project {
  id: string;
  title: string;
  organization: string;
  description: string;
  link: string;
}

export interface Education {
  id: string;
  degree: string;
  institution: string;
  startYear: string;
  endYear: string;
  gpa: string;
}

export interface ResumeData {
  photo: string | null;
  personal: {
    fullName: string;
    email: string;
    phone: string;
    location: string;
    linkedin: string;
    portfolio: string;
    summary: string;
  };
  experiences: Experience[];
  projects: Project[];
  educations: Education[];
  skills: string[];
}

export const defaultResumeData: ResumeData = {
  photo: null,
  personal: {
    fullName: "Abinesh Gowtham",
    email: "abineshms7@gmail.com",
    phone: "9629428592",
    location: "Chennai",
    linkedin: "https://www.linkedin.com/in/abinesh-gowtham-043696212/",
    portfolio: "https://abinesh-gowtham.netlify.app/",
    summary: `Results-driven Frontend Developer with 4 years of experience designing and developing scalable,
high-performance web applications using React.js, TypeScript, JavaScript (ES6+), HTML5, and CSS3. Proficient in
responsive UI/UX design, API integration, state management (Redux Toolkit), and performance optimisation. Adept at
implementing React Hooks, unit testing with Jest and React Testing Library, and ensuring cross-browser compatibility
and accessibility. Experienced in Agile environments, collaborating with cross-functional teams to deliver quality
software that enhances user engagement and business value`,
  },
  experiences: [
    { id: "exp-1", jobTitle: "System Engineer", companyName: "Infosys Ltd", startDate: "2021-12-13", endDate: "2022-12-05", description: `● Contributed to frontend maintenance and UI bug resolution for enterprise applications, ensuring stable user
experiences and reducing defect rates by 30%.
● Performed manual and functional testing across multiple environments, validating UI responsiveness and
workflow correctness.
● Worked directly with clients and cross-functional teams to prioritise enhancements and ensure timely sprint
deliveries.
` },
    { id: "exp-2", jobTitle: "Software Development Engineer", companyName: "AVRL", startDate: "2022-12-05", endDate: "2025-10-31", description: `● Designed and developed interactive, responsive React components for the company’s Performance
Management Suite, covering Home Feed, Rewards, and Feedback modules used by 1,000+ employees.
● Implemented infinite scroll and lazy loading, improving feed performance and load efficiency by 80%.
● Utilised React 18 features and Redux Toolkit for efficient state management, reducing component re-render
time.
● Developed a decision tree automation system integrated with customer pricing APIs, enabling real-time bid
generation and failure reason analysis for logistics clients.
● Collaborated with backend and QA teams in an Agile/Scrum en` },
  ],
  projects: [
    { id: "proj-1", title: "NA", organization: "AVRL", description: "NA", link: "NA" },
  ],
  educations: [
    { id: "edu-1", degree: "B.E", institution: "Madras Institute of Technology", startYear: "2017", endYear: "2021", gpa: "7.2" },
  ],
  skills: ["HTML","CSS","Javascript","Reactjs"],
};