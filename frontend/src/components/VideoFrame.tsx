'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Loader2, Upload, Image as ImageIcon } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import StepsAnalysisCard from './StepsAnalysisCard'
import { DEFAULT_TEXT } from '@/types/constants'
// import { useAppContext } from '@/contexts/App'


export default function VideoFrame() {
    const [video, setVideo] = useState<File | null>(null)
    const [processing, setProcessing] = useState(false)
    const [content, setContent] = useState(DEFAULT_TEXT)
    const [selectedFrames, setSelectedFrames] = useState<string[]>([])
    // const { llmData } = useAppContext()

    const onDrop = useCallback((acceptedFiles: File[]) => {
        if (acceptedFiles[0]) {
            setVideo(acceptedFiles[0])
            setSelectedFrames([])
        }
    }, [])

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'video/*': [] },
        multiple: false
    })

    const processVideo = async () => {
        setProcessing(true)

        const formData = new FormData();
        formData.append("file", video as Blob);

        try {
            const response = await fetch('http://79.117.18.84:38414/video-to-frames/', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                console.log(data)
                setSelectedFrames(data.frames)
                const output = JSON.parse(data.output)
                setContent(JSON.stringify(output, null, 2))
            } else {
                // setError('Failed to process video');
            }
        } catch (error) {
            console.log(error)
            // setError('Error uploading video');
        } finally {
            setProcessing(false)
        }
    }

    return (
        <div className="container mx-auto p-4">
            <div className="flex flex-col lg:flex-row gap-4">
                <div className="flex flex-col lg:flex-col gap-4">

                    <Card className="w-full max-w-2xl mx-auto md:min-w-[670px]">
                <CardHeader>
                    <CardTitle className="text-2xl font-bold text-center">Video Frame Selector</CardTitle>
                </CardHeader>
                <CardContent>
                    <div
                        {...getRootProps()}
                        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${isDragActive ? 'border-primary bg-primary/10' : 'border-gray-300 hover:border-primary'
                            }`}
                    >
                        <input {...getInputProps()} />
                        <Upload className="mx-auto h-12 w-12 text-gray-400" />
                        <p className="mt-2 text-sm text-gray-600">Drag and drop a video file here, or click to select a file</p>
                    </div>
                    {video && (
                        <div className="mt-4">
                            <video src={URL.createObjectURL(video)} controls className="w-full rounded-lg" />
                            <p className="mt-2 text-sm text-gray-600 text-center">{video.name}</p>
                        </div>
                    )}
                </CardContent>
                <CardFooter className="flex flex-col items-center">
                    <Button onClick={processVideo} disabled={!video || processing} className="w-full max-w-xs mb-4">
                        {processing ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Processing...
                            </>
                        ) : (
                            'Process Video'
                        )}
                    </Button>
                    {processing && (
                        <div className="w-full max-w-xs space-y-4" aria-live="polite" aria-busy={processing}>
                                    <div className="w-full h-2 bg-secondary rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-primary rounded-full animate-indeterminate-progress"
                                            style={{
                                                width: '50%',
                                            }}
                                        />
                                    </div>
                            <div className="flex justify-between items-center">
                                <div className="space-y-2">
                                    <p className="text-sm font-medium">Analyzing video...</p>
                                    <p className="text-xs text-muted-foreground">Selecting key frames</p>
                                </div>
                                <div className="flex space-x-1">
                                    <div className="w-2 h-2 bg-primary rounded-full animate-pulse" style={{ animationDelay: '0ms' }}></div>
                                    <div className="w-2 h-2 bg-primary rounded-full animate-pulse" style={{ animationDelay: '300ms' }}></div>
                                    <div className="w-2 h-2 bg-primary rounded-full animate-pulse" style={{ animationDelay: '600ms' }}></div>
                                </div>
                            </div>
                        </div>
                    )}
                </CardFooter>
            </Card>
            {selectedFrames.length > 0 && (
                <Card className="mt-4 w-full max-w-2xl mx-auto">
                    <CardHeader>
                        <CardTitle className="text-xl font-semibold">Selected Key Frames</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                            {selectedFrames.map((frame, index) => (
                                <div key={index} className="flex flex-col items-center">
                                    <div className="relative w-full aspect-video bg-gray-100 rounded-lg overflow-hidden">
                                        <ImageIcon className="absolute inset-0 m-auto text-gray-400" size={48} />
                                        <img
                                            src={`data:image/jpeg;base64,${frame}`}
                                            alt={`Selected frame`}
                                            className="absolute inset-0 w-full h-full object-cover"
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}
                </div>
                <StepsAnalysisCard content={content} />
            </div>
        </div>
    )
}