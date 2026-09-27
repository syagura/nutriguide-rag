import { useEffect, useState } from 'react'
import './LoadingStatus.css'

const STAGES = [
    'Menganalisis pertanyaan...',
    'Mencari informasi dari sumber terpercaya...',
    'Membaca dokumen...',
    'Menyusun jawaban...',
]

const STAGE_DURATION_MS = 2200

const LoadingStatus = () => {
    const [stageIndex, setStageIndex] = useState(0)

    useEffect(() => {
        const interval = setInterval(() => {
            setStageIndex(prev => (prev < STAGES.length - 1 ? prev + 1 : prev))
        }, STAGE_DURATION_MS)

        return () => clearInterval(interval)
    }, [])

    return (
        <div className='loading-status'>
            <div className='loading-dots'>
                <span className='dot'/>
                <span className='dot'/>
                <span className='dot'/>
            </div>
            <span className='loading-status-text'>{STAGES[stageIndex]}</span>
        </div>
    )
}

export default LoadingStatus
