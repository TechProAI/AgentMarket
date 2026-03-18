import './ResumeBuilderAgent.css'

interface Step {
  path: string,
  label: string,
  number: number
}

const steps:Step[] = [
  { path: "/", label: "Photo", number: 1 },
  { path: "/personal-details", label: "Personal", number: 2 },
  { path: "/experience", label: "Experience", number: 3 },
  { path: "/projects", label: "Projects", number: 4 },
  { path: "/education", label: "Education", number: 5 },
  { path: "/skills", label: "Skills", number: 6 },
  { path: "/preview", label: "Preview", number: 7 },
];

const ResumeBuilderAgent = () => {

  return (
    <div className='resume-container' id='resume-section'>
      <div className='resume-section'>
        <div><h1>Resume Builder</h1></div>
        <div>Create your professional resume in minutes</div>
        <div></div>
      </div>
    </div>
  )
}

export default ResumeBuilderAgent