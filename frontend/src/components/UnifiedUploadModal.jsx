import React, { useState, useRef } from 'react';
import { Button } from './ui/button';
import { Upload, FileText, Database, MapPin, X, ChevronRight } from 'lucide-react';

const UnifiedUploadModal = ({ 
  isOpen, 
  onClose, 
  trails = [], 
  onUploadGPX, 
  onUploadLiDAR, 
  onUploadXLSX,
  currentTrailId = null,
  isUploading = false 
}) => {
  const [uploadStep, setUploadStep] = useState('type'); // 'type', 'trail', 'upload'
  const [selectedType, setSelectedType] = useState('');
  const [selectedTrailId, setSelectedTrailId] = useState(currentTrailId);
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  
  const fileInputRef = useRef(null);

  if (!isOpen) return null;

  const reset = () => {
    setUploadStep('type');
    setSelectedType('');
    setSelectedTrailId(currentTrailId);
    setSelectedFile(null);
    setDragActive(false);
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  const uploadTypes = [
    {
      id: 'gpx',
      title: 'New Trail (GPX)',
      description: 'Upload a GPX file to create a new trail',
      icon: MapPin,
      accept: '.gpx',
      color: 'blue',
      needsTrail: false
    },
    {
      id: 'lidar',
      title: 'LiDAR Data',
      description: 'Add high-resolution elevation data to an existing trail',
      icon: Database,
      accept: '.las,.laz',
      color: 'green',
      needsTrail: true
    },
    {
      id: 'xlsx',
      title: 'Elevation Profile',
      description: 'Add detailed elevation analysis from XLSX data',
      icon: FileText,
      accept: '.xlsx,.xls',
      color: 'purple',
      needsTrail: true
    }
  ];

  const selectedTypeConfig = uploadTypes.find(t => t.id === selectedType);

  const handleTypeSelect = (type) => {
    setSelectedType(type.id);
    if (type.needsTrail) {
      setUploadStep('trail');
    } else {
      setUploadStep('upload');
    }
  };

  const handleTrailSelect = () => {
    if (!selectedTrailId) {
      alert('Please select a trail first');
      return;
    }
    setUploadStep('upload');
  };

  const handleFileSelect = (file) => {
    if (!file) return;
    
    const config = selectedTypeConfig;
    if (!config) return;

    // Validate file type
    const fileName = file.name.toLowerCase();
    const validExtensions = config.accept.split(',').map(ext => ext.trim());
    const isValidFile = validExtensions.some(ext => fileName.endsWith(ext.replace('.', '')));
    
    if (!isValidFile) {
      alert(`Please select a valid ${config.accept} file`);
      return;
    }

    setSelectedFile(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files[0];
    handleFileSelect(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    try {
      switch (selectedType) {
        case 'gpx':
          await onUploadGPX(selectedFile);
          break;
        case 'lidar':
          await onUploadLiDAR(selectedFile, selectedTrailId);
          break;
        case 'xlsx':
          await onUploadXLSX(selectedFile, selectedTrailId);
          break;
      }
      handleClose();
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  const currentTrail = trails.find(t => t.id === currentTrailId);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 sm:p-6 border-b">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900">
            Upload Trail Data
          </h2>
          <button
            onClick={handleClose}
            className="p-1 hover:bg-gray-100 rounded"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 sm:p-6">
          {/* Step 1: Type Selection */}
          {uploadStep === 'type' && (
            <div className="space-y-4">
              <p className="text-sm text-gray-600 mb-6">
                What would you like to upload?
              </p>
              
              {uploadTypes.map((type) => {
                const Icon = type.icon;
                return (
                  <button
                    key={type.id}
                    onClick={() => handleTypeSelect(type)}
                    className={`w-full p-4 border-2 rounded-lg hover:border-${type.color}-300 hover:bg-${type.color}-50 transition-colors text-left group`}
                  >
                    <div className="flex items-center">
                      <div className={`p-2 rounded-lg bg-${type.color}-100 text-${type.color}-600 mr-3`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-medium text-gray-900">{type.title}</h3>
                          {type.needsTrail && (
                            <span className="px-2 py-1 text-xs font-medium text-white bg-gradient-to-r from-purple-500 to-purple-600 rounded-full">
                              Enhancement
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-500">{type.description}</p>
                      </div>
                      <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-gray-600" />
                    </div>
                  </button>
                );
              })}
            </div>
          )}

          {/* Step 2: Trail Selection */}
          {uploadStep === 'trail' && selectedTypeConfig && (
            <div className="space-y-4">
              <div className="flex items-center mb-4">
                <div className={`p-2 rounded-lg bg-${selectedTypeConfig.color}-100 text-${selectedTypeConfig.color}-600 mr-3`}>
                  <selectedTypeConfig.icon className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">{selectedTypeConfig.title}</h3>
                  <p className="text-sm text-gray-500">Select which trail to enhance</p>
                </div>
              </div>

              {/* Pre-selected trail suggestion */}
              {currentTrail && (
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg mb-4">
                  <p className="text-sm text-blue-800">
                    💡 Currently viewing: <strong>{currentTrail.name}</strong>
                  </p>
                  <button
                    onClick={() => setSelectedTrailId(currentTrail.id)}
                    className="text-sm text-blue-600 hover:text-blue-800 mt-1"
                  >
                    Use this trail →
                  </button>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Trail
                </label>
                <select
                  value={selectedTrailId || ""}
                  onChange={(e) => setSelectedTrailId(e.target.value ? parseInt(e.target.value) : null)}
                  className="w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Choose a trail...</option>
                  {trails.map((trail) => (
                    <option key={trail.id} value={trail.id}>
                      {trail.name} ({trail.distance_km?.toFixed(2)} km, {trail.elevation_gain?.toFixed(0)}m gain)
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex gap-3 mt-6">
                <Button
                  onClick={() => setUploadStep('type')}
                  variant="outline"
                  className="flex-1"
                >
                  Back
                </Button>
                <Button
                  onClick={handleTrailSelect}
                  disabled={!selectedTrailId}
                  className="flex-1"
                >
                  Continue
                </Button>
              </div>
            </div>
          )}

          {/* Step 3: File Upload */}
          {uploadStep === 'upload' && selectedTypeConfig && (
            <div className="space-y-4">
              <div className="flex items-center mb-4">
                <div className={`p-2 rounded-lg bg-${selectedTypeConfig.color}-100 text-${selectedTypeConfig.color}-600 mr-3`}>
                  <selectedTypeConfig.icon className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">{selectedTypeConfig.title}</h3>
                  {selectedTrailId && (
                    <p className="text-sm text-gray-500">
                      For: {trails.find(t => t.id === selectedTrailId)?.name}
                    </p>
                  )}
                </div>
              </div>

              {/* File Drop Zone */}
              <div
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
                onDragEnter={() => setDragActive(true)}
                onDragLeave={() => setDragActive(false)}
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  dragActive 
                    ? 'border-blue-400 bg-blue-50' 
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <Upload className="w-8 h-8 text-gray-400 mx-auto mb-4" />
                <p className="text-sm text-gray-600 mb-2">
                  Drag and drop your {selectedTypeConfig.accept} file here
                </p>
                <p className="text-xs text-gray-500 mb-4">or</p>
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  variant="outline"
                  size="sm"
                >
                  Browse Files
                </Button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept={selectedTypeConfig.accept}
                  onChange={(e) => handleFileSelect(e.target.files[0])}
                  className="hidden"
                />
              </div>

              {/* Selected File Display */}
              {selectedFile && (
                <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center">
                    <FileText className="w-5 h-5 text-green-600 mr-2" />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-green-800">{selectedFile.name}</p>
                      <p className="text-xs text-green-600">
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                </div>
              )}

              <div className="flex gap-3 mt-6">
                <Button
                  onClick={() => {
                    if (selectedTypeConfig.needsTrail) {
                      setUploadStep('trail');
                    } else {
                      setUploadStep('type');
                    }
                  }}
                  variant="outline"
                  className="flex-1"
                >
                  Back
                </Button>
                <Button
                  onClick={handleUpload}
                  disabled={!selectedFile || isUploading}
                  className="flex-1"
                >
                  {isUploading ? 'Uploading...' : 'Upload'}
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UnifiedUploadModal;