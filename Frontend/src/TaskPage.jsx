import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function TaskPage() {
  const [id, setId] = useState("0");
  const [tasks, setTasks] = useState([]);
  const [form, setForm] = useState({ title: '', description: '',task : '', etc: '', due_date: '' });
  const navigate = useNavigate();
  const token = localStorage.getItem('token');

  useEffect(() => {
    if (!token) navigate('/login');
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try{
    const res = await axios.get("http://localhost:8000/task_get", {headers: {Authorization: "Bearer "+ token}});
    setTasks(res.data.task);
    }catch(err){
    console.log("Error:", err.response.data);
    if (err.status == 401){
      console.log("Unauthorized")
       localStorage.removeItem("token")
       navigate("/login")
     }
    }
  };

  const handleCreateTask = async () => {
    try {
      // const user_id = parseJwt(token).id;
      
        await axios.post('http://localhost:8000/task_add', form, {headers: {Authorization: "Bearer "+ token}});
    
    fetchTasks();
    } catch (err) {
      console.log("Error:", err);
      alert('Task creation failed');
    }
  };
  
  const handleUpdateTask = async (title) => {
    try {
        await axios.patch('http://localhost:8000/task_update', {title, status:"Complete"}, {headers: {Authorization: "Bearer "+ token}});
    fetchTasks();
    } catch (err) {
      console.log("Error:", err);
      alert('Task update failed');
    }
  };
  const handleDelete = async (id) => {
    try{
    await axios.delete(`http://localhost:8000/task_delete/${id}`, {headers: {Authorization: "Bearer "+ token}});
    fetchTasks();
    }catch(err){
      console.log("Error:", err);
    }
  };

  const exportTasks = async () => {
    const res = await axios.get(`http://localhost:8000/task_excel/`, { responseType: 'blob',headers: {Authorization: "Bearer "+ token} });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'tasks.xlsx');
    document.body.appendChild(link);
    link.click();
  };

  return (
    <div className="task-page">
      <h2>Your Tasks</h2>
      <button onClick={()=>{setForm({ title: '', description: '',task : '', etc: '', due_date: '' })}}>Create New Task</button>
      <form onSubmit={handleCreateTask}>
        <input type="text" placeholder="Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
        <input type="text" placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} required />
        <input type="number" placeholder="Effort (days)" value={form.etc} onChange={(e) => setForm({ ...form, etc: e.target.value })} required />
        <input type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} required />
        <button type="submit" onClick={handleCreateTask}>Create Task</button>
      </form>

      <button onClick={exportTasks} style={{ marginTop: '20px' }}>Export to Excel</button>

      <ul>
        {tasks.map(task => (
          <li key={task.id}>
            <strong>{task.title}</strong> - {task.description} | Due: {task.due_date}
            <button onClick={()=>{handleUpdateTask(task.title)}}>Update</button>
            <button onClick={() =>{handleDelete(task.id)}}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default TaskPage;
